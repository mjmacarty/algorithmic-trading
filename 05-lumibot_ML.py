from datetime import datetime
from datetime import timedelta
from lumibot.backtesting import PolygonDataBacktesting
from lumibot.credentials import IS_BACKTESTING
from lumibot.strategies import Strategy
from lumibot.traders import Trader
from ml_class import ML


class MLTrader(Strategy):
    parameters = {
        "symbol" : "GLD",
        "start" : "2020-01-01",
        "lags" : 7
    }

    
    
    def initialize(self):
        self.sleeptime = "15M"
        self.minutes_before_closing = 15
        self.vars.signal = None
        
        
    
    def before_market_opens(self):
        self.vars.model = ML(self.parameters['symbol'], 
                             self.parameters['start'], 
                             self.get_datetime().strftime("%Y-%m-%d"))
        self.vars.model.create_lags(self.parameters['lags'])
        self.vars.model.train_model(self.parameters['lags'])
        self.vars.signal = self.vars.model.forecast(self.parameters['lags'])


    def before_starting_trading(self):
        self.vars.first_trade = True


    
    def on_trading_iteration(self):
        if self.vars.first_trade:
            self.vars.first_trade = False    
            symbol = self.parameters['symbol']
            quantity = self.trade_quantity(symbol)
        
            
            if self.vars.signal[0] == 1:
                order = self.create_order(symbol, quantity, "buy")
                self.submit_order(order)
            else:
                order = self.create_order(symbol, quantity, "sell")
                self.submit_order(order)

        # if self.check_time():
        #     self.before_market_closes()
    
    
    def trade_quantity(self, symbol):
        price = self.get_last_price(symbol)
        cash = self.get_cash()
        return cash * 0.5 // price


    def check_time(self):
        now = datetime.now()
        if now.hour == 15 and now.minute >= 45:
            return True
        return False


    def before_market_closes(self):
        self.sell_all()       


     



if __name__ == "__main__":
    if IS_BACKTESTING:
        start = datetime(2024, 10, 31)
        end = datetime(2024,12, 31)
        MLTrader.run_backtest(
            PolygonDataBacktesting,
            start,
            end,
            benchmark_asset= "GLD"
        )
        
    else:
        strategy = MLTrader() 
        trader = Trader()
        trader.add_strategy(strategy)
        trader.run_all()                                 