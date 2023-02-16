from config import ALPACA_CONFIG
from datetime import datetime
from lumibot.backtesting import YahooDataBacktesting
from lumibot.brokers import Alpaca
from lumibot.strategies import Strategy
from lumibot.traders import Trader


class BuyHold(Strategy):

    def initialize(self):
        self.sleeptime = "1D"

    def on_trading_iteration(self):
        if self.first_iteration:
            symbol = "GOOG"
            price = self.get_last_price(symbol)
            quantity = self.cash // price
            order = self.create_order(symbol, quantity, "buy")
            self.submit_order(order)


if __name__ == "__main__":
    trade = False
    if trade:
        broker = Alpaca(ALPACA_CONFIG)
        strategy = BuyHold(broker=broker)
        trader = Trader()
        trader.add_strategy(strategy)
        trader.run_all()
    else:
        start = datetime(2022, 1, 1)
        end = datetime(2022, 12, 31)
        BuyHold.backtest(
            YahooDataBacktesting,
            start,
            end
        )
