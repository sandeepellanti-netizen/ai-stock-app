
import pandas as pd

def rsi(df):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs.iloc[-1]))

def ema(df):
    return df['Close'].ewm(span=20).mean().iloc[-1]

def macd(df):
    exp1 = df['Close'].ewm(span=12).mean()
    exp2 = df['Close'].ewm(span=26).mean()
    return (exp1 - exp2).iloc[-1]

def trend(df):
    return "UPTREND" if df['Close'].iloc[-1] > df['Close'].rolling(20).mean().iloc[-1] else "DOWNTREND"

def signal(df):
    r = rsi(df)
    if r < 30:
        return "BUY"
    elif r > 70:
        return "SELL"
    return "HOLD"

def support_resistance(df):
    support = df['Low'].rolling(20).min().iloc[-1]
    resistance = df['High'].rolling(20).max().iloc[-1]
    return support, resistance
