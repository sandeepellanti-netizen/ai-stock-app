
import yfinance as yf
from services.indicators import support_resistance

stocks = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS"]

def scan_market():
    results=[]
    for s in stocks:
        try:
            df=yf.download(s, period="3mo")

            last=df['Close'].iloc[-1]
            volume=df['Volume'].iloc[-1]
            avg_vol=df['Volume'].rolling(20).mean().iloc[-1]

            support, resistance = support_resistance(df)

            breakout_resistance = last > resistance
            breakout_support = last < support
            volume_spike = volume > 1.5 * avg_vol

            if breakout_resistance and volume_spike:
                signal = "STRONG BUY (Resistance Breakout)"
            elif breakout_support:
                signal = "BREAKDOWN (Bearish)"
            else:
                signal = "NO TRADE"

            results.append({
                "symbol": s,
                "price": round(float(last),2),
                "support": round(float(support),2),
                "resistance": round(float(resistance),2),
                "volume_spike": volume_spike,
                "signal": signal
            })
        except:
            continue
    return results
