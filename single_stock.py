import quantstats as qs

stock ="SPY"

portfolio = qs.utils.download_returns(stock, period='3y')
# print(portfolio.head())

# print("Available stats:")
# print([fx for fx in dir(qs.stats) if fx[0] != "_"])

print(f"Sharpe: {qs.stats.sharpe(portfolio)}")
print(f"Best Day: {qs.stats.best(portfolio)}")
print(f"Best Day: {qs.stats.best(portfolio, aggregate='M')}")

qs.extend_pandas()

print(portfolio.cagr())
print(portfolio.max_drawdown())
print(portfolio.monthly_returns())
