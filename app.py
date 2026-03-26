from flask import Flask, request, jsonify, render_template
import yfinance as yf
import pandas as pd
import requests

app = Flask(__name__)

# 🔑 Your News API Key
NEWS_API_KEY = "a0ffc5cef7fc4ea58edae0d50e263f2b"


# =========================
# 📊 HELPER FUNCTIONS
# =========================

def calculate_rsi(df):
    try:
        delta = df["Close"].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        value = rsi.iloc[-1]
        if pd.isna(value):
            return 50  # fallback neutral

        return float(value)
    except:
        return 50


def support_resistance(df):
    try:
        support = df["Low"].rolling(20).min().iloc[-1]
        resistance = df["High"].rolling(20).max().iloc[-1]

        if pd.isna(support) or pd.isna(resistance):
            return 0, 0

        return float(support), float(resistance)
    except:
        return 0, 0


def get_news(symbol):
    try:
        # 🔥 Remove .NS for news search
        symbol = symbol.replace(".NS", "")

        url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey={NEWS_API_KEY}"
        res = requests.get(url, timeout=5).json()

        articles = []
        for a in res.get("articles", [])[:5]:
            articles.append({
                "title": a.get("title", ""),
                "url": a.get("url", "#")
            })

        return articles
    except:
        return []


def analyze_sentiment(news):
    if not news:
        return "Neutral"

    text = " ".join([n["title"] for n in news]).lower()

    pos = ["gain", "bull", "rise", "growth", "profit"]
    neg = ["fall", "bear", "loss", "drop", "decline"]

    score = 0
    for w in pos:
        if w in text:
            score += 1
    for w in neg:
        if w in text:
            score -= 1

    if score > 0:
        return "Positive"
    elif score < 0:
        return "Negative"
    return "Neutral"


# =========================
# 🏠 HOME
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# 📈 ANALYZE STOCK (FIXED)
# =========================

@app.route("/analyze")
def analyze():
    try:
        symbol_input = request.args.get("symbol", "").upper().strip()

        if not symbol_input:
            return jsonify({"error": "Please enter a stock name"})

        # Ensure NSE format
        symbol = symbol_input if symbol_input.endswith(".NS") else symbol_input + ".NS"

        ticker = yf.Ticker(symbol)
        df = ticker.history(period="6mo")

        # 🔴 HARD FIX: empty / insufficient data
        if df is None or df.empty or len(df) < 50:
            return jsonify({"error": "Invalid stock or insufficient data"})

        # 🔴 SAFE extraction
        close_series = df["Close"].dropna()
        if close_series.empty:
            return jsonify({"error": "Price data unavailable"})

        close = float(close_series.iloc[-1])

        # RSI
        rsi = calculate_rsi(df)

        # Trend
        try:
            ma20 = float(df["Close"].rolling(20).mean().iloc[-1])
            trend = "UPTREND" if close > ma20 else "DOWNTREND"
        except:
            trend = "UNKNOWN"

        # Signal
        if rsi < 30:
            signal = "BUY"
        elif rsi > 70:
            signal = "SELL"
        else:
            signal = "HOLD"

        # Predictions
        pred_1w = close * 1.02
        pred_1m = close * 1.05

        # News + Sentiment
        news = get_news(symbol)
        sentiment = analyze_sentiment(news)

        return jsonify({
            "symbol": symbol,
            "price": round(close, 2),
            "rsi": round(rsi, 2),
            "trend": trend,
            "signal": signal,
            "sentiment": sentiment,
            "pred_1w": round(pred_1w, 2),
            "pred_1m": round(pred_1m, 2),
            "news": news
        })

    except Exception as e:
        print("ANALYZE ERROR:", str(e))
        return jsonify({"error": str(e)})


# =========================
# 🔍 SCANNER (STABLE)
# =========================

@app.route("/scanner")
def scanner():
    try:
        stocks = [
            "RELIANCE.NS", "TCS.NS", "INFY.NS",
            "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS",
            "ITC.NS", "LT.NS"
        ]

        results = []

        for s in stocks:
            try:
                df = yf.Ticker(s).history(period="3mo")

                if df is None or df.empty or len(df) < 20:
                    continue

                close = float(df["Close"].dropna().iloc[-1])
                volume = float(df["Volume"].iloc[-1])
                avg_vol = float(df["Volume"].rolling(20).mean().iloc[-1])

                support, resistance = support_resistance(df)

                breakout = close > resistance
                volume_spike = volume > 1.5 * avg_vol

                if breakout and volume_spike:
                    signal = "STRONG BUY"
                else:
                    signal = "NO TRADE"

                results.append({
                    "symbol": s,
                    "price": round(close, 2),
                    "support": round(support, 2),
                    "resistance": round(resistance, 2),
                    "volume_spike": volume_spike,
                    "signal": signal
                })

            except Exception as e:
                print("SCANNER ERROR:", s, str(e))
                continue

        return jsonify(results)

    except Exception as e:
        print("SCANNER FAIL:", str(e))
        return jsonify([])


# =========================
# 🚀 RUN APP (RENDER SAFE)
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
