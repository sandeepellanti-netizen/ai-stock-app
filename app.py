from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
from services.indicators import get_indicators
from services.prediction import predict_prices
from services.news import get_news_sentiment

app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def home():
    result=None
    symbol=None

    if request.method=="POST":
        symbol=request.form.get("symbol")

        # Force Indian stocks (.NS)
        if not symbol.endswith(".NS"):
            symbol = symbol + ".NS"

        data=yf.download(symbol, period="6mo")

        if isinstance(data.columns, pd.MultiIndex):
            data.columns=data.columns.get_level_values(0)

        close=data["Close"].dropna()

        indicators=get_indicators(data)
        prediction=predict_prices(data)
        news=get_news_sentiment(symbol)

        result={
            "price":float(close.iloc[-1]),
            "rsi":indicators["rsi"],
            "trend":indicators["trend"],
            "signal":indicators["signal"],
            "week":prediction["week"],
            "month":prediction["month"],
            "sentiment":news["sentiment"],
            "headlines":news["headlines"]
        }

    return render_template("index.html", result=result, symbol=symbol)

@app.route("/chart")
def chart():
    symbol=request.args.get("symbol")

    if not symbol.endswith(".NS"):
        symbol = symbol + ".NS"

    data=yf.download(symbol, period="6mo")

    if isinstance(data.columns, pd.MultiIndex):
        data.columns=data.columns.get_level_values(0)

    return jsonify({
        "close":data["Close"].dropna().tolist(),
        "dates":data.index.strftime("%Y-%m-%d").tolist()
    })

if __name__=="__main__":
    app.run()
