
from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
import os

from services.indicators import rsi, ema, macd, signal, trend
from services.ml_model import predict_lightweight
from services.news import get_news, analyze_sentiment
from services.scanner import scan_market

app = Flask(__name__)

@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    return response

@app.route("/", methods=["GET","POST"])
def home():
    result=None

    if request.method=="POST":
        symbol=request.form.get("symbol") + ".NS"
        df=yf.download(symbol, period="6mo")

        if isinstance(df.columns, pd.MultiIndex):
            df.columns=df.columns.get_level_values(0)

        news_data = get_news(symbol)

        result={
            "price":round(float(df["Close"].iloc[-1]),2),
            "rsi":round(rsi(df),2),
            "ema":round(ema(df),2),
            "macd":round(macd(df),2),
            "signal":signal(df),
            "trend":trend(df),
            "prediction":predict_lightweight(df),
            "news":news_data,
            "sentiment":analyze_sentiment(news_data)
        }

    return render_template("index.html", result=result)

@app.route("/scanner")
def scanner():
    return jsonify(scan_market())

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
