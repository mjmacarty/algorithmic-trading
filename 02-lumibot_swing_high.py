from datetime import datetime
from lumibot.backtesting import BacktestingBroker, PolygonDataBacktesting
from lumibot.credentials import IS_BACKTESTING
from lumibot.strategies import Strategy
from lumibot.traders import Trader


class SwingHigh(Strategy):
    parameters = {
        "symbol" : "NVDA",
        "quantity" : 100
    }

    def initialize(self):
        self.sleeptime = "5S"
        self.vars.data = []
        self.vars.order_number = 0


    def on_trading_iteration(self):
        symbol = self.parameters['symbol']
        entry_price = self.get_last_price(symbol)
        self.log_message(f"Position: {self.get_position(symbol)}")
        self.vars.data.append(entry_price)

        if len(self.vars.data) > 3:
            temp = self.vars.data[-3:]
            if temp[-1] > temp[1] > temp[0] and self.get_cash() > 20000:
                self.log_message(f"Last three prices: {temp}")
                order = self.create_order(symbol, self.parameters['quantity'], 'buy')
                self.submit_order(order)
                self.vars.order_number += 1

                if self.vars.order_number == 1:
                    entry_price = temp[-1]

        if self.get_position(symbol) and self.vars.data[-1] < entry_price * .9975:
            self.sell_all()
            order_number = 0
        elif self.get_position(symbol) and self.vars.data[-1] > entry_price * 1.01:
            self.sell_all()
            order_number = 0

    def before_market_closes(self):
        self.sell_all()
        self.vars.order_number = 0
                        

if __name__ == "__main__":
    if IS_BACKTESTING: 
        start = datetime(2024,11,17)
        end = datetime(2024,11,24)
        SwingHigh.backtest(
            PolygonDataBacktesting,
            start,
            end,
            benchmark_asset = "NVDA"
        )
    else:    
        strategy = SwingHigh()
        trader = Trader()
        trader.add_strategy(strategy)
        trader.run_all()
        
