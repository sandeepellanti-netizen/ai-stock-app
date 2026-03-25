from flask import Flask, request, render_template_string
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import requests

app = Flask(__name__)

ALPHA_API_KEY = "9W9FBF5Z3R407LRU"
NEWS_API_KEY = "a0ffc5cef7fc4ea58edae0d50e263f2b"

ts = TimeSeries(key=ALPHA_API_KEY, output_format='pandas')

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Ultimate AI Trading App</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <h2>💎 Ultimate AI Trading App</h2>
    <form method="post">
        <input type="text" name="stock" placeholder="IBM or RELIANCE.BSE" required>
        <button type="submit">Analyze</button>
    </form>

    {% if suggestion %}
        <h3>📊 Signal: {{suggestion}}</h3>
        <h3>💰 Price: {{price}}</h3>
        <h3>📉 RSI: {{rsi}}</h3>
        <h3>📊 MACD: {{macd}}</h3>
        <h3>📈 Trend: {{trend}}</h3>
        <img src="data:image/png;base64,{{chart}}" width="100%"/>
        <h3>📰 News:</h3>
        {% for n in news %}
            <p>{{n}}</p>
        {% endfor %}
    {% endif %}
</body>
</html>
"""

def get_stock(symbol):
    data, _ = ts.get_daily(symbol=symbol, outputsize='compact')
    data = data.sort_index()
    return data['4. close']

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    return (100 - (100 / (1 + rs))).iloc[-1]

def macd(series):
    ema12 = series.ewm(span=12).mean()
    ema26 = series.ewm(span=26).mean()
    return (ema12 - ema26).iloc[-1]

def trend(series):
    ma20 = series.rolling(20).mean().iloc[-1]
    price = series.iloc[-1]
    return "UP 📈" if price > ma20 else "DOWN 📉"

def chart(series):
    plt.figure()
    series.plot()
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

def news(stock):
    url = f"https://newsapi.org/v2/everything?q={stock}&apiKey={NEWS_API_KEY}"
    res = requests.get(url).json()
    articles = res.get("articles", [])[:5]
    headlines = []
    score = 0
    for a in articles:
        title = a.get("title", "")
        headlines.append(title)
        t = title.lower()
        if any(w in t for w in ["gain","rise","profit"]):
            score += 1
        if any(w in t for w in ["fall","loss","drop"]):
            score -= 1
    return headlines, score

@app.route("/", methods=["GET","POST"])
def home():
    suggestion = ""
    price = ""
    rsi_val = ""
    macd_val = ""
    trend_val = ""
    img = ""
    headlines = []

    if request.method == "POST":
        stock = request.form["stock"]
        try:
            data = get_stock(stock)
            price = round(data.iloc[-1], 2)
            rsi_val = round(rsi(data), 2)
            macd_val = round(macd(data), 2)
            trend_val = trend(data)
            headlines, news_score = news(stock)
            img = chart(data)

            confidence = 0
            confidence += 2 if rsi_val < 30 else -2 if rsi_val > 70 else 0
            confidence += 1 if macd_val > 0 else -1
            confidence += 1 if "UP" in trend_val else -1
            confidence += news_score

            if confidence >= 3:
                suggestion = "STRONG BUY 🚀"
            elif confidence >= 1:
                suggestion = "BUY 📈"
            elif confidence <= -3:
                suggestion = "STRONG SELL 📉"
            elif confidence <= -1:
                suggestion = "SELL 📉"
            else:
                suggestion = "HOLD 🤝"

        except Exception as e:
            suggestion = "Error: " + str(e)

    return render_template_string(
        HTML,
        suggestion=suggestion,
        price=price,
        rsi=rsi_val,
        macd=macd_val,
        trend=trend_val,
        chart=img,
        news=headlines
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
