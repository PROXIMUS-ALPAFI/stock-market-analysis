from flask import Flask, request, jsonify, render_template
import yfinance as yf
import pandas as pd
import mysql.connector
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from joblib import dump, load
import os
from flask_cors import CORS
from sklearn.metrics import r2_score, accuracy_score, f1_score

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# MySQL Database connection
db = mysql.connector.connect(
    host="localhost",
    user="stockuser",
    password="your_password",
    database="stock_auth"
)


cursor = db.cursor(dictionary=True)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']  # plain text

    try:
        query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, email, password))
        db.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "Error registering user"}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    try:
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if not user or user['password'] != password:
            return jsonify({"message": "Invalid credentials"}), 401

        return jsonify({"message": "Login successful", "user_id": user['id']}), 200
    except Exception as e:
        print("Login error:", e)
        return jsonify({"message": "Server error"}), 500

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
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    df['DMA_50_200'] = df['SMA_50'] - df['SMA_200']

    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

    df['Middle_Band'] = df['Close'].rolling(window=20).mean()
    df['Upper_Band'] = df['Middle_Band'] + (df['Close'].rolling(window=20).std() * 2)
    df['Lower_Band'] = df['Middle_Band'] - (df['Close'].rolling(window=20).std() * 2)

    df['Volume_Change'] = df['Volume'].pct_change()

    news = stock.news
    analyzer = SentimentIntensityAnalyzer()
    sentiment_scores = [analyzer.polarity_scores(article['title'])['compound'] for article in news if 'title' in article]
    df['Sentiment'] = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0

    df['Future Close'] = df['Close'].shift(-5)
    df.dropna(inplace=True)

    filename = f"data/{symbol}_data.csv"
    df.to_csv(filename, index=False)

    df_head = df[['Date', 'Close', 'SMA_50', 'SMA_200', 'DMA_50_200', 'RSI', 'MACD', 'Signal_Line',
                  'Upper_Band', 'Lower_Band', 'Volume_Change', 'Sentiment', 'Future Close']].tail().to_dict(orient='records')

    return jsonify({
        "message": f"Stock data saved as {filename}!",
        "data": df_head
    })

@app.route('/train_model', methods=['POST'])
def train_model():
    symbol = request.json.get('symbol', 'AAPL')
    file_path = f"data/{symbol}_data.csv"

    if not os.path.exists(file_path):
        return jsonify({"error": "Stock data not found! Fetch data first."}), 400

    df = pd.read_csv(file_path)
    features = ['SMA_50', 'SMA_200', 'DMA_50_200', 'RSI', 'MACD', 'Signal_Line',
                'Upper_Band', 'Lower_Band', 'Volume_Change', 'Sentiment']
    X = df[features]
    y = df['Future Close']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    dump(model, f"data/{symbol}_stock_model.joblib")

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
    data = request.json
    symbol = data.get('symbol')
    user_id = data.get('user_id')

    if not symbol or not user_id:
        return jsonify({"error": "Stock symbol and user_id are required!"}), 400

    file_path = f"data/{symbol}_data.csv"
    if not os.path.exists(file_path):
        return jsonify({"error": "Train the model first!"}), 400

    df = pd.read_csv(file_path)
    features = ['SMA_50', 'SMA_200', 'DMA_50_200', 'RSI', 'MACD', 'Signal_Line',
                'Upper_Band', 'Lower_Band', 'Volume_Change', 'Sentiment']
    X = df[features]

    model = load(f"data/{symbol}_stock_model.joblib")
    latest_data = X.tail(1)
    predicted_price = float(model.predict(latest_data)[0])  # fix here

    # Save to history table
    try:
        cursor.execute(
            "INSERT INTO user_stock_history (user_id, symbol, predicted_price) VALUES (%s, %s, %s)",
            (user_id, symbol, predicted_price)
        )
        db.commit()
    except Exception as e:
        print("History Save Error:", e)

    return jsonify({"predicted_exit_price": predicted_price})

@app.route('/user_history/<int:user_id>', methods=['GET'])
def get_user_history(user_id):
    try:
        cursor.execute(
            "SELECT symbol, predicted_price, requested_at FROM user_stock_history WHERE user_id = %s ORDER BY requested_at DESC",
            (user_id,)
        )
        history = cursor.fetchall()
        return jsonify({"history": history})
    except Exception as e:
        print("Fetch history error:", e)
        return jsonify({"message": "Could not retrieve history."}), 500

if __name__ == '__main__':
    if not os.path.exists("data"):
        os.makedirs("data")
    app.run(debug=True)
