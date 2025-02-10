import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC
import yfinance as yf


symbol ="GLD"
start = "2020-01-01"
end = "2024-12-31"

data = yf.download(symbol, start=start, end=end)
data['returns'] = data['Close'].pct_change()

lags = 5

columns = [f"lag_{lag}" for lag in range(1, lags+1)]
counter = 1
for column in columns:
    data[column] = data['returns'].shift(counter)
    counter += 1

data = data[['Close'] + columns + ['returns']] 
data.dropna(inplace=True)

data[columns] = np.where(data[columns] > 0, 1, 0)
data['direction'] = np.where(data['returns'] > 0, 1, -1)

model = SVC(C=1.0, kernel='linear', gamma='auto', probability=True)
split = int(0.8 * len(data))
train = data.iloc[:split].copy()
model.fit(train[columns], train['direction'])
win = accuracy_score(train['direction'], model.predict(train[columns]))


print(f"Training accuracy: {win}")
test = data.iloc[split:].copy()
test['prediction'] = model.predict(test[columns])
print(test.head(10))
print(f"Test accuracy: {accuracy_score(test['direction'], test['prediction'])}")

forecast = data.iloc[-1].to_list()
forecast = forecast[1:]
direction = 1 if data["returns"].iloc[-1] > 0 else 0
forecast.append(direction)
forecast = pd.DataFrame(forecast[:lags], columns).T
print(model.predict(forecast))
print(model.predict_proba(forecast))     
