import matplotlib.pyplot as plt
from openbb_terminal.sdk import openbb
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose, STL

df = openbb.economy.unemp(2010)
print(df.head())
df = df.set_index("date")[:"2019-12-31"].sort_index()
print(df.head())

df["rolling_mean"] = df["unemp"].rolling(window=12).mean()
df["rolling_std"] = df["unemp"].rolling(window=12).std()
#df.plot(title="Unemployment rate")


# decomposition_results = seasonal_decompose(
#     df["unemp"], 
#     model="additive"
# ).plot()
stl_decomposition = STL(df[["unemp"]]).fit()
stl_decomposition.plot().suptitle("STL Decomposition")

plt.show()