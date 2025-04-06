import numpy as np
import pandas as pd
import yfinance as yf
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import joblib

MODEL_PATH = "lstm_model.h5"
SCALER_PATH = "scaler.pkl"

def get_stock_data(symbol, start="2020-01-01"):
    stock = yf.Ticker(symbol)
    data = stock.history(period="5y")  # Get last 5 years
    return data[["Close"]]

def prepare_data(data, window_size=50):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    joblib.dump(scaler, SCALER_PATH)  # Save scaler for future use

    X, y = [], []
    for i in range(window_size, len(scaled_data)):
        X.append(scaled_data[i - window_size:i, 0])
        y.append(scaled_data[i, 0])

    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))  # Reshape for LSTM input
    return X, y

# Fetch and prepare data
symbol = "AAPL"
data = get_stock_data(symbol)
X_train, y_train = prepare_data(data)

# Define LSTM model
model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)),
    Dropout(0.2),
    LSTM(50, return_sequences=False),
    Dropout(0.2),
    Dense(25),
    Dense(1)
])

model.compile(optimizer="adam", loss="mean_squared_error")
model.fit(X_train, y_train, epochs=50, batch_size=32, verbose=1)

# Save the trained model
model.save(MODEL_PATH)
print("LSTM model trained and saved!")
