from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
from services.indicators import *
from services.ml_model import predict_lightweight
from services.news import get_news, analyze_sentiment
from services.scanner import scan_market

app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def home():
    result=None

    if request.method=="POST":
        symbol=request.form.get("symbol") + ".NS"
        df=yf.download(symbol, period="1y")

        if isinstance(df.columns, pd.MultiIndex):
            df.columns=df.columns.get_level_values(0)

        pred = predict_lightweight(df)

        result={
            "price":round(float(df["Close"].iloc[-1]),2),
            "rsi":rsi(df),
            "ema":ema(df),
            "macd":macd(df),
            "signal":signal(df),
            "trend":trend(df),
            "prediction":pred,
            "news":get_news(symbol),
            "sentiment":analyze_sentiment(get_news(symbol))
        }

    return render_template("index.html", result=result)

@app.route("/scanner")
def scanner():
    return jsonify(scan_market())

if __name__=="__main__":
    app.run()
