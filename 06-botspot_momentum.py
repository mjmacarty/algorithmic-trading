import datetime as dt
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from lumibot.entities import Asset, TradingFee, Order
from lumibot.credentials import IS_BACKTESTING

# Import data backtesting class for minute-level data (using Polygon for options and minute data)
from lumibot.backtesting import PolygonDataBacktesting


class AGGScalpingStrategy(Strategy):
    """
    This strategy implements a simple day trading scalping approach for AGG based on minute data momentum.
    It calculates momentum as the difference between the current price and the moving average of the last 5 minutes.
    If the price is above the moving average by a set threshold, the bot will go long; if it falls below, it will exit the position.
    In addition, the strategy now includes risk management rules to limit losses to -0.25% and take profits at +0.5% relative to the entry price, and
    it also forces the exit of any open positions at the end of the trading day.

    This code was refined based on the user prompt: 'close open positions at the end of the day and limit losses to -.0025, take profits .005'
    """

    # Extend parameters to include risk management settings
    parameters = {
        'momentum_threshold': 0.001,  # threshold relative to current price (e.g., 0.1% upward movement)
        'trade_quantity': 100,         # number of shares to buy/sell per trade
        'stop_loss': -0.0025,          # maximum loss threshold (e.g., -0.25%)
        'take_profit': 0.005           # target profit threshold (e.g., +0.5%)
    }

    def initialize(self):
        # Set sleeptime to 1 minute intervals since we use minute data
        self.sleeptime = "1M"
        # Define the asset AGG for this strategy
        self.asset = Asset("AGG", asset_type=Asset.AssetType.STOCK)
        # Log the initialization
        self.log_message("AGG Scalping Strategy Initialized. Monitoring minute data momentum.")
        
        # Initialize a persistent variable to store the entry price of our open position
        # This variable will help compare current price to the entry price for risk management
        self.vars.entry_price = None

    def on_trading_iteration(self):
        # Get the current price of AGG
        current_price = self.get_last_price(self.asset)
        if current_price is None:
            self.log_message("Current price not available, skipping iteration.")
            return

        # Retrieve any existing position for AGG
        position = self.get_position(self.asset)
        position_qty = position.quantity if position is not None else 0

        # If we already have a position, ensure we record the entry price if not already recorded
        if position_qty > 0:
            if self.vars.entry_price is None:
                # Record the entry price when a position is first opened
                self.vars.entry_price = current_price
                self.log_message(f"Recording entry price: {self.vars.entry_price:.4f}")
            else:
                # Calculate the profit (or loss) percentage relative to the entry price
                profit_pct = (current_price - self.vars.entry_price) / self.vars.entry_price
                # Check risk management thresholds: take profit or stop loss
                if profit_pct >= self.parameters['take_profit'] or profit_pct <= self.parameters['stop_loss']:
                    self.log_message(f"Risk management triggered: Profit/Loss = {profit_pct:.4f}. Exiting position.")
                    order = self.create_order(self.asset, position_qty, Order.OrderSide.SELL)
                    self.submit_order(order)
                    # Reset the entry price after exiting the position
                    self.vars.entry_price = None
                    return  # Skip further processing this iteration

        # Retrieve historical minute data for the last 5 minutes to compute a simple moving average
        bars = self.get_historical_prices(self.asset, 5, "minute")
        if bars is None or len(bars.df) < 5:
            self.log_message("Not enough historical data, skipping iteration.")
            return
        
        # Calculate the moving average price over the last 5 minutes
        df = bars.df
        moving_average = df['close'].mean()

        # Calculate the momentum as the difference between current price and the moving average
        momentum = current_price - moving_average

        # Log the current price, moving average, and momentum
        self.log_message(f"Current price: {current_price:.4f}, Moving Average: {moving_average:.4f}, Momentum: {momentum:.4f}")

        # Get strategy parameters
        threshold = self.parameters.get('momentum_threshold', 0.001) * current_price
        quantity = self.parameters.get('trade_quantity', 100)

        # If momentum is significantly positive and we are not in a long position, then buy
        if momentum > threshold and position_qty <= 0:
            cash = self.get_cash()
            if cash < current_price * quantity:
                self.log_message("Not enough cash to execute trade.")
                return
            order = self.create_order(self.asset, quantity, Order.OrderSide.BUY)
            self.log_message(f"Submitting BUY order for {quantity} shares at price {current_price:.4f}")
            self.submit_order(order)
            # Record the entry price for risk management after entering a new position
            self.vars.entry_price = current_price

        # If momentum is negative and we have a long position, then exit the position by selling all
        elif momentum < 0 and position_qty > 0:
            order = self.create_order(self.asset, position_qty, Order.OrderSide.SELL)
            self.log_message(f"Submitting SELL order for {position_qty} shares at price {current_price:.4f} due to negative momentum")
            self.submit_order(order)
            # Clear the entry price once the position is closed
            self.vars.entry_price = None

        else:
            self.log_message("No trading signal triggered this iteration.")

    def before_market_closes(self):
        """
        Lifecycle method to ensure all open positions are closed before the market closes.
        This helps to avoid overnight exposures.
        """
        position = self.get_position(self.asset)
        if position is not None and position.quantity > 0:
            self.log_message(f"Market closing: Exiting open position of {position.quantity} shares.")
            order = self.create_order(self.asset, position.quantity, Order.OrderSide.SELL)
            self.submit_order(order)
            # Reset the recorded entry price as the position has been closed
            self.vars.entry_price = None


if __name__ == "__main__":
    if IS_BACKTESTING:
        # Backtesting section using minute-level data from Polygon
        trading_fee = TradingFee(percent_fee=0.001)  # Example trading fee of 0.1%
        # Run backtest with SPY as the benchmark asset
        result = AGGScalpingStrategy.backtest(
            datasource_class=PolygonDataBacktesting,
            benchmark_asset=Asset("SPY", asset_type=Asset.AssetType.STOCK),
            buy_trading_fees=[trading_fee],
            sell_trading_fees=[trading_fee],
            parameters=AGGScalpingStrategy.parameters,
            budget=100000,
            backtesting_start=dt.datetime(2025, 3, 17),
            backtesting_end=dt.datetime(2025, 3, 21)
        )
    else:
        # Live Trading section
        trader = Trader()
        strategy = AGGScalpingStrategy(
            quote_asset=Asset("USD", asset_type=Asset.AssetType.FOREX)  # Quote asset for live trading remains USD
        )
        trader.add_strategy(strategy)
        trader.run_all()