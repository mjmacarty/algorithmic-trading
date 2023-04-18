import datetime as dt
from dateutil.relativedelta import relativedelta
import os
import pandas as pd
# import pandas_datareader as pdr
import numpy as np
import quantstats as qs
import webbrowser as web
import yfinance as yf


def ma_cross_strategy(ticker, slow=200, fast=50, end=None, period=3):
    if not end:
        end = dt.date.today()
    start = end - relativedelta(years=period)

    data = pd.DataFrame(yf.download(ticker, start=start, end=end)["Close"])
    data[f'{fast}-day'] = data.Close.rolling(fast).mean()
    data[f'{slow}-day'] = data.Close.rolling(slow).mean()
    data['returns'] = np.log(data.Close).diff()
    data['strategy'] = np.where(data[f'{fast}-day'] > data[f'{slow}-day'], 1, 0)
    data['strategy'] = np.where(data[f'{fast}-day'] < data[f'{slow}-day'], -1, data['strategy'])
    strategy = data['returns'] * data['strategy']
    return strategy


gld_cross = ma_cross_strategy("GLD", slow=21, fast=9, period=3)
gld_cross.index = gld_cross.index.tz_localize(None)
gld = qs.utils.download_returns("GLD", period='3y')
gld.index = gld.index.tz_localize(None)

qs.extend_pandas()

qs.reports.html(gld_cross, gld, output="output/gld_cross.html",
                download_filename="output/gld_cross.html")
web.open_new(f"file:///{os.getcwd()}/output/gld_cross.html")

