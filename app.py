from flask import Flask, request, render_template_string
import yfinance as yf
import pandas as pd

app = Flask(__name__)

def rsi(data, period=14):
    close = data["Close"].dropna()
    delta = close.diff()

    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

def trend(data):
    close = data["Close"].dropna()

    if len(close) < 20:
        return "Not enough data"

    latest = float(close.iloc[-1])
    past = float(close.iloc[-20])

    if latest > past:
        return "UPTREND 📈"
    else:
        return "DOWNTREND 📉"

@app.route("/", methods=["GET", "POST"])
def home():
    result = ""
    if request.method == "POST":
        symbol = request.form.get("symbol")

        try:
            data = yf.download(symbol, period="3mo", interval="1d")

            if data.empty:
                result = "Invalid stock symbol"
            else:
                price = float(data["Close"].iloc[-1])
                rsi_val = float(rsi(data).iloc[-1])
                trend_val = trend(data)

                result = f"Price: {price:.2f} <br> RSI: {rsi_val:.2f} <br> Trend: {trend_val}"

        except Exception as e:
            result = f"Error: {str(e)}"

    return render_template_string("""
    <h2>Ultimate AI Trading App</h2>
    <form method="post">
        <input name="symbol" placeholder="AAPL or RELIANCE.NS">
        <button type="submit">Analyze</button>
    </form>
    <p>{{result|safe}}</p>
    """, result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
