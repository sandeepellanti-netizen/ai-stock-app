import yfinance as yf
from services.indicators import support_resistance

stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]  # keep small for Render

def scan_market():
    results = []

    for s in stocks:
        try:
            df = yf.download(s, period="3mo", progress=False)

            if df.empty:
                continue

            last = float(df['Close'].iloc[-1])
            volume = float(df['Volume'].iloc[-1])
            avg_vol = float(df['Volume'].rolling(20).mean().iloc[-1])

            support, resistance = support_resistance(df)

            breakout_resistance = last > resistance
            breakout_support = last < support
            volume_spike = volume > 1.5 * avg_vol

            if breakout_resistance and volume_spike:
                signal = "STRONG BUY"
            elif breakout_support:
                signal = "BREAKDOWN"
            else:
                signal = "NO TRADE"

            results.append({
                "symbol": s,
                "price": round(last, 2),
                "support": round(float(support), 2),
                "resistance": round(float(resistance), 2),
                "volume_spike": volume_spike,
                "signal": signal
            })

        except Exception as e:
            print("Scanner error:", s, str(e))  # 🔥 IMPORTANT DEBUG
            continue

    return results
