from flask import Flask, request, jsonify, render_template
import yfinance as yf
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from joblib import dump, load
import os
from flask_cors import CORS
from sklearn.metrics import mean_absolute_error, r2_score,accuracy_score,f1_score


app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)
@app.route('/get_stock_data', methods=['POST'])
def get_stock_data():
    symbol = request.json.get('symbol', None)

    if not symbol:
        return jsonify({"error": "Stock symbol is required!"}), 400

    stock = yf.Ticker(symbol)
    df = stock.history(period="5y")

    if df.empty:
        return jsonify({"error": f"No data found for {symbol}!"}), 400

    df.reset_index(inplace=True)
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')  # Formatting date

    # Compute Indicators
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    df['DMA_50_200'] = df['SMA_50'] - df['SMA_200']

    # RSI Calculation
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # MACD Calculation
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # Bollinger Bands
    df['Middle_Band'] = df['Close'].rolling(window=20).mean()
    df['Upper_Band'] = df['Middle_Band'] + (df['Close'].rolling(window=20).std() * 2)
    df['Lower_Band'] = df['Middle_Band'] - (df['Close'].rolling(window=20).std() * 2)

    # Volume Change
    df['Volume_Change'] = df['Volume'].pct_change()

    # Sentiment Analysis
    news = stock.news
    analyzer = SentimentIntensityAnalyzer()
    sentiment_scores = [analyzer.polarity_scores(article['title'])['compound'] for article in news if
                        'title' in article]
    df['Sentiment'] = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0

    # Future Price Prediction Target
    df['Future Close'] = df['Close'].shift(-5)
    df.dropna(inplace=True)

    # Save data to CSV
    filename = f"data/{symbol}_data.csv"
    df.to_csv(filename, index=False)

    # Convert the first few rows to a dictionary and return it as part of the response
    df_head = df[
        ['Date', 'Close', 'SMA_50', 'SMA_200', 'DMA_50_200', 'RSI', 'MACD', 'Signal_Line', 'Upper_Band', 'Lower_Band',
         'Volume_Change', 'Sentiment', 'Future Close']].tail().to_dict(orient='records')

    return jsonify({
        "message": f"Stock data saved as {filename}!",
        "data": df_head  # Sending the first few rows of data including Date
    })

@app.route('/train_model', methods=['POST'])
def train_model():
    symbol = request.json.get('symbol', 'AAPL')
    file_path = f"data/{symbol}_data.csv"

    if not os.path.exists(file_path):
        return jsonify({"error": "Stock data not found! Fetch data first."}), 400

    df = pd.read_csv(file_path)

    # Feature selection
    features = ['SMA_50', 'SMA_200', 'DMA_50_200', 'RSI', 'MACD', 'Signal_Line',
                'Upper_Band', 'Lower_Band', 'Volume_Change', 'Sentiment']

    X = df[features]
    y = df['Future Close']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train Model
    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    # Save the model
    dump(model, f"data/{symbol}_stock_model.joblib")

    # Evaluate Model
    predictions = model.predict(X_test)

    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    y_test_binarized = (y_test > y_test.median()).astype(int)
    predictions_binarized = (predictions > y_test.median()).astype(int)
    accuracy = accuracy_score(y_test_binarized, predictions_binarized)
    f1 = f1_score(y_test_binarized, predictions_binarized)

    return jsonify({
        "message": "Model trained!",
        "mse": mse,
        "r2": r2,
        "accuracy": accuracy,
        "f1": f1
    })


@app.route('/predict_exit', methods=['POST'])
def predict_exit():
    symbol = request.json.get('symbol', None)

    if not symbol:
        return jsonify({"error": "Stock symbol is required!"}), 400

    file_path = f"data/{symbol}_data.csv"
    if not os.path.exists(file_path):
        return jsonify({"error": "Train the model first!"}), 400

    df = pd.read_csv(file_path)
    features = ['SMA_50', 'SMA_200', 'DMA_50_200', 'RSI', 'MACD', 'Signal_Line',
                'Upper_Band', 'Lower_Band', 'Volume_Change', 'Sentiment']

    X = df[features]

    model = load("data/stock_model.joblib")
    latest_data = X.iloc[-1].values.reshape(1, -1)
    predicted_price = model.predict(latest_data)

    return jsonify({"predicted_exit_price": predicted_price[0]})


if __name__ == '__main__':
    if not os.path.exists("data"):
        os.makedirs("data")
    app.run(debug=True)
