from flask import Flask, request, jsonify
import yfinance as yf
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)


def get_stock_record(ticker: str, start: str = "2020-01-01", end: str = "2025-01-01"):
    stock = yf.Ticker(ticker)
    df = stock.history(start=start, end=end)

    # Compute technical indicators manually
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    df['DMA_50_200'] = df['SMA_50'] - df['SMA_200']  # Double Moving Average

    # Relative Strength Index (RSI)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Moving Average Convergence Divergence (MACD)
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # Bollinger Bands
    df['Middle_Band'] = df['Close'].rolling(window=20).mean()
    df['Upper_Band'] = df['Middle_Band'] + (df['Close'].rolling(window=20).std() * 2)
    df['Lower_Band'] = df['Middle_Band'] - (df['Close'].rolling(window=20).std() * 2)

    # Compute price change over the next 5 days
    df['Future Change %'] = df['Close'].pct_change(periods=5).shift(-5) * 100

    # Fetch news articles
    news = stock.news
    analyzer = SentimentIntensityAnalyzer()
    sentiment_scores = []

    # Check the structure of a single news article
    for article in news:
        if 'title' in article:
            score = analyzer.polarity_scores(article['title'])['compound']
            sentiment_scores.append(score)

    # Add the average sentiment score as a new feature
    df['Sentiment'] = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0

    # Labeling strategy
    def classify_stock(change, sentiment):
        if change > 5 and sentiment > 0.1:
            return "Strong Buy"
        elif change < -5 and sentiment < -0.1:
            return "Sell"
        else:
            return "Hold"

    # Apply sentiment and price change to classification
    df['Label'] = df.apply(lambda row: classify_stock(row['Future Change %'], row['Sentiment']), axis=1)

    return df


@app.route('/analyze_stock', methods=['GET'])
def analyze_stock():
    ticker_symbol = request.args.get('symbol')  # Get symbol from URL query parameters
    if not ticker_symbol:
        return jsonify({"error": "Stock symbol is required!"}), 400

    # Get the stock data and analysis
    df = get_stock_record(ticker_symbol)

    # Get the latest classification for the stock
    today_label = df['Label'].iloc[-1]

    # Save the DataFrame to a CSV file
    csv_filename = f"{ticker_symbol}_stock_data.csv"
    df.to_csv(csv_filename)

    # Return the analysis as a JSON response
    response = {
        'ticker': ticker_symbol,
        'classification': today_label,
        'data': df.tail(1).to_dict(orient='records'),  # Return the most recent row of data
        'csv_file': csv_filename  # Send the filename as part of the response
    }

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
