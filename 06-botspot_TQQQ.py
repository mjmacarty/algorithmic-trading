import datetime as dt
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from lumibot.entities import Asset, TradingFee, Order
from lumibot.credentials import IS_BACKTESTING
import pandas as pd

"""
This code was generated based on the user prompt: 'Make a bot that trades TQQQ based on the 200 day moving average. When TQQQ is above its 200 day moving average use all the cash in the account to buy TQQQ, and when it’s below the 200 day moving average, sell and just hold cash'

Strategy Description:
---------------------
This strategy calculates the 200-day Simple Moving Average (SMA) for TQQQ each trading iteration. If the current price is above the SMA, the bot uses all available cash to buy TQQQ. If the price falls below the SMA, it sells any existing TQQQ positions and holds cash only.

DISCLAIMER: This code is for educational and testing purposes only and is not intended as investment advice.
"""


class TQQQ200MAStrategy(Strategy):
    def initialize(self):
        # Set the time interval for the strategy to run (daily in this case)
        self.sleeptime = "1D"

    def on_trading_iteration(self):
        # Define the asset to trade (TQQQ stock)
        asset = Asset("TQQQ", asset_type=Asset.AssetType.STOCK)

        # Fetch the historical daily prices for the past 200 days
        bars = self.get_historical_prices(asset, 200, "day")
        if bars is None:
            self.log_message("Historical data not available, skipping iteration.")
            return
        df = bars.df
        if len(df) < 200:
            self.log_message("Insufficient data to compute the 200-day SMA, skipping iteration.")
            return

        # Calculate the 200-day Simple Moving Average (SMA)
        df["200_sma"] = df["close"].rolling(window=200).mean()
        current_sma = df["200_sma"].iloc[-1]
        
        # Get the most recent closing price
        current_price = self.get_last_price(asset)
        if current_price is None or pd.isna(current_sma):
            self.log_message("Missing current price or SMA data, skipping iteration.")
            return

        # Decision making based on the current price and 200-day SMA
        if current_price > current_sma:
            # When price is above the SMA, use all available cash to buy TQQQ
            pos = self.get_position(asset)
            if pos is None or pos.quantity == 0:
                cash = self.get_cash()
                if cash > 0:
                    shares = int(cash // current_price)  # Determine how many shares we can buy with available cash
                    if shares > 0:
                        order = self.create_order(asset, shares, Order.OrderSide.BUY)
                        self.submit_order(order)
                        self.log_message(f"Buying {shares} shares of TQQQ at {current_price}")
                    else:
                        self.log_message("Not enough cash to buy even a single share.")
                else:
                    self.log_message("No cash available to buy TQQQ.")
            else:
                self.log_message("Already holding TQQQ. Continuing to hold the position.")
        else:
            # When price is below the SMA, sell any TQQQ position to hold cash
            pos = self.get_position(asset)
            if pos is not None and pos.quantity > 0:
                shares = pos.quantity
                order = self.create_order(asset, shares, Order.OrderSide.SELL)
                self.submit_order(order)
                self.log_message(f"Selling {shares} shares of TQQQ at {current_price}")
            else:
                self.log_message("No TQQQ position to sell. Holding cash.")


if __name__ == "__main__":
    if IS_BACKTESTING:
        # Backtesting setup using YahooDataBacktesting for stock data
        from lumibot.backtesting import YahooDataBacktesting
        trading_fee = TradingFee(percent_fee=0.001)  # Example trading fee used for both buying and selling
        params = {}  # No extra parameters are required in this strategy
        result = TQQQ200MAStrategy.backtest(
            datasource_class=YahooDataBacktesting,
            benchmark_asset=Asset("QQQ", asset_type=Asset.AssetType.STOCK),
            buy_trading_fees=[trading_fee],
            sell_trading_fees=[trading_fee],
            parameters=params,
            backtesting_start= dt.datetime(2020, 1, 1),
            backtesting_end= dt.datetime(2025, 1, 1)
        )
    else:
        # Live trading setup; the broker and live configurations are automatically handled
        trader = Trader()
        strategy = TQQQ200MAStrategy(
            quote_asset=Asset("USD", asset_type=Asset.AssetType.FOREX)  # Set the quote asset to USD
        )
        trader.add_strategy(strategy)
        trader.run_all()