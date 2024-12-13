import matplotlib.pyplot as plt
import yfinance as yf

gld = yf.download("GLD", "2023-01-01")
gld["9-day"] = gld["Close"].rolling(9).mean()
gld["21-day"] = gld["Close"].rolling(21).mean()

plt.plot(gld['Close'][-90:])
plt.plot(gld['9-day'][-90:])
plt.plot(gld['21-day'][-90:])
plt.show()
