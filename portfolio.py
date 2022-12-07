import quantstats as qs


qs.extend_pandas()

index = {"SPY": 1.3, "AGG": -.3}

portfolio = qs.utils.make_index(index, period='3y')
portfolio.index = portfolio.index.tz_localize(None)
portfolio.plot_earnings(start_balance= 10000, savefig="output/portfolio_earnings.png")
portfolio.plot_monthly_heatmap(savefig="output/portfolio_heat.png")
#print(portfolio.head())