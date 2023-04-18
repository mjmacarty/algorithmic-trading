import numpy as np
import pandas as pd
import pandas_datareader as pdr
import yfinance as yf


gld = pd.DataFrame(yf.download("GLD", "2022-01-01")['Close'])
gld['9-day'] = gld['Close'].rolling(9).mean()
gld['21-day'] = gld['Close'].rolling(21).mean()
gld['Signal'] = np.where(np.logical_and(gld['9-day'] > gld['21-day'],
                         gld['9-day'].shift(1) < gld['21-day'].shift(1)),
                         "BUY", None)
gld['Signal'] = np.where(np.logical_and(gld['9-day'] < gld['21-day'],
                         gld['9-day'].shift(1) > gld['21-day'].shift(1)),
                         "SELL", gld['Signal'])

def signal(df, start="2022-05-16", end="2022-06-16"):
    df = pd.DataFrame(yf.download("GLD", start, end)['Close'])
    df['9-day'] = df['Close'].rolling(9).mean()
    df['21-day'] = df['Close'].rolling(21).mean()
    df['Signal'] = np.where(np.logical_and(df['9-day'] > df['21-day'],
                            df['9-day'].shift(1) < df['21-day'].shift(1)),
                            "BUY", None)
    df['Signal'] = np.where(np.logical_and(df['9-day'] < df['21-day'],
                            df['9-day'].shift(1) > df['21-day'].shift(1)),
                            "SELL", df['Signal'])
    return df, df.iloc[-1].Signal

print(gld)
print("-" * 10)
print(gld.iloc[-1].Signal)
gld.to_csv('gld_signal.csv')

data, sig = signal(gld)
print(data)
print(sig)
print(len(data))



