from flask import Flask, request, render_template_string
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import requests

app = Flask(__name__)

NEWS_API_KEY = "a0ffc5cef7fc4ea58edae0d50e263f2b"

def get_stock(symbol):
    data = yf.download(symbol, period="3mo", interval="1d")
    if data.empty:
        raise Exception("Invalid stock symbol")
    return data

def rsi(data, period=14):
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def macd(data):
    exp1 = data["Close"].ewm(span=12).mean()
    exp2 = data["Close"].ewm(span=26).mean()
    return exp1 - exp2

def trend(data):
    if data["Close"].iloc[-1] > data["Close"].iloc[-20]:
        return "UPTREND 📈"
    else:
        return "DOWNTREND 📉"

def news(symbol):
    url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey={NEWS_API_KEY}"
    res = requests.get(url).json()

    articles = res.get("articles", [])[:5]
    score = 0
    headlines = []

    for a in articles:
        t = a["title"].lower()
        headlines.append(a["title"])

        if any(w in t for w in ["gain", "rise", "profit"]):
            score += 1
        if any(w in t for w in ["fall", "loss", "drop"]):
            score -= 1

    return headlines, score

def plot_chart(data):
    plt.figure()
    data["Close"].tail(50).plot()
    plt.title("Price Chart")

    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)

    img = base64.b64encode(buf.getvalue()).decode()
    plt.close()

    return img

@app.route("/", methods=["GET", "POST"])
def home():
    result = ""

    if request.method == "POST":
        stock = request.form["stock"]

        try:
            data = get_stock(stock)

            price = round(data["Close"].iloc[-1], 2)
            rsi_val = round(rsi(data).iloc[-1], 2)
            macd_val = round(macd(data).iloc[-1], 2)
            trend_val = trend(data)

            headlines, score = news(stock)
            img = plot_chart(data)

            signal = "BUY 🚀" if score > 0 else "SELL 🔻"

            result = f"""
            <h3>Signal: {signal}</h3>
            <p>💰 Price: {price}</p>
            <p>📉 RSI: {rsi_val}</p>
            <p>📊 MACD: {macd_val}</p>
            <p>📈 Trend: {trend_val}</p>
            <img src="data:image/png;base64,{img}" width="300"/>
            <h4>📰 News:</h4>
            <ul>
            {''.join([f"<li>{h}</li>" for h in headlines])}
            </ul>
            """

        except Exception as e:
            result = f"<p>Error: {str(e)}</p>"

    return render_template_string(f"""
    <h1>💎 Ultimate AI Trading App</h1>
    <form method="POST">
        <input name="stock" placeholder="AAPL or RELIANCE.NS"/>
        <button type="submit">Analyze</button>
    </form>
    {result}
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
