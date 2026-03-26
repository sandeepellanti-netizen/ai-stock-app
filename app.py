from flask import Flask, request, render_template_string
import yfinance as yf
import pandas as pd
import requests
import os

app = Flask(__name__)

# ---------------- NEWS FUNCTIONS ----------------
NEWS_API_KEY = "YOUR_NEWS_API_KEY"

def get_news(symbol):
    try:
        url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey={NEWS_API_KEY}"
        response = requests.get(url).json()

        articles = []
        for article in response.get("articles", [])[:5]:
            articles.append({
                "title": article["title"],
                "url": article["url"]
            })

        return articles
    except:
        return []

def analyze_sentiment(news_list):
    if not news_list:
        return "Neutral"

    text = " ".join([n["title"] for n in news_list]).lower()

    positive = ["gain", "bull", "rise", "profit", "growth"]
    negative = ["fall", "bear", "loss", "drop", "decline"]

    score = 0

    for w in positive:
        if w in text:
            score += 1
    for w in negative:
        if w in text:
            score -= 1

    if score > 0:
        return "Positive"
    elif score < 0:
        return "Negative"
    return "Neutral"


# ---------------- STOCK ANALYSIS ----------------
def analyze_stock(symbol):
    df = yf.download(symbol, period="3mo")

    df["RSI"] = 100 - (100 / (1 + df["Close"].pct_change().rolling(14).mean()))

    price = float(df["Close"].iloc[-1])
    rsi = float(df["RSI"].iloc[-1])

    trend = "UPTREND" if df["Close"].iloc[-1] > df["Close"].iloc[-20] else "DOWNTREND"
    signal = "BUY" if rsi < 30 else "SELL" if rsi > 70 else "HOLD"

    # Predictions
    pred_week = price * 1.02
    pred_month = price * 1.05

    # News
    news = get_news(symbol)
    sentiment = analyze_sentiment(news)

    return {
        "price": round(price,2),
        "rsi": round(rsi,2),
        "trend": trend,
        "signal": signal,
        "pred_week": round(pred_week,2),
        "pred_month": round(pred_month,2),
        "news": news,
        "sentiment": sentiment
    }


# ---------------- UI ----------------
HTML = """
<h1>🇮🇳 AI Trading Platform</h1>

<form method="post">
<input name="symbol" placeholder="RELIANCE.NS">
<button>Analyze</button>
</form>

{% if data %}
<h2>💰 Price: {{data.price}}</h2>
<p>📊 RSI: {{data.rsi}}</p>
<p>📉 Trend: {{data.trend}}</p>
<p>📌 Signal: {{data.signal}}</p>

<h3>🔮 Predictions</h3>
<p>1 Week: {{data.pred_week}}</p>
<p>1 Month: {{data.pred_month}}</p>

<h3>📰 Sentiment: {{data.sentiment}}</h3>

<h3>News</h3>
<ul>
{% for n in data.news %}
<li><a href="{{n.url}}" target="_blank">{{n.title}}</a></li>
{% endfor %}
</ul>
{% endif %}
"""


@app.route("/", methods=["GET","POST"])
def home():
    data = None
    if request.method == "POST":
        symbol = request.form["symbol"]
        data = analyze_stock(symbol)

    return render_template_string(HTML, data=data)


# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
