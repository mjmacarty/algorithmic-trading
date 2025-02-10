import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC
import yfinance as yf


class ML:
    
    
    def __init__(self, symbol, start, end):
        self.symbol = symbol
        self.start = start
        self.end = end
        self.data = yf.download(symbol, start=self.start, end=self.end )['Close']
        self.data = pd.DataFrame(self.data)
        self.data['returns'] = np.log(self.data['Close']).diff()


    def create_lags(self, lags):
        columns = [f"lag_{lag}"for lag in range(1, lags + 1)]
        counter = 1
        for column in columns:
            self.data[column] = self.data['returns'].shift(counter)
            counter += 1

        self.data = self.data[['Close'] + columns + ['returns']] 
        self.data.dropna(inplace=True)
        self.data[columns] = np.where(self.data[columns] > 0, 1, 0)
        self.data['direction'] = np.where(self.data['returns'] > 0, 1, -1)    
        #print(self.data[columns + ['direction']].head())
        return columns

    
    def train_model(self, lags):
        columns = self.create_lags(lags)
        model = SVC(C=1, kernel='linear', gamma='auto', probability= True)
        split = int(len(self.data)* 0.80)
        train = self.data.iloc[:split].copy()
        model.fit(train[columns], train['direction'])
        win = accuracy_score(train['direction'], model.predict(train[columns]))
        #print(f"Win train{win}")
        return model, columns, split

    
    def test_model(self, lags):
        model, columns, split = self.train_model(lags)
        test = self.data.iloc[split:].copy()
        test['prediction'] = model.predict(test[columns])
        #print(test.tail(10))
        win_predict = accuracy_score(test['direction'], (test['prediction']))
        #print(f"Test win: {win_predict}")
        #return model.predict.iloc[-1]

    
    def forecast(self, lags):
        model, columns, split = self.train_model(lags)
        forecast = self.data.iloc[-1].to_list()
        forecast = forecast[1:]
        direction = 1 if self.data['returns'].iloc[-1] > 0 else 0
        forecast.append(direction)
        forecast = pd.DataFrame(forecast[:lags], columns).T
        return model.predict(forecast).item(), model.predict_proba(forecast)[0][1]

       
        
# To test uncomment code below        
if __name__ == '__main__':
    
    ml = ML('SPY', '2020-01-01', '2025-01-15')
    ml.create_lags(10)
    ml.train_model(10)
    ml.test_model(10)
    forecast = ml.forecast(10)
    print(ml.forecast(10))       