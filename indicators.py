def get_indicators(data):
    close=data["Close"].dropna()

    delta=close.diff()
    gain=(delta.where(delta>0,0)).rolling(14).mean()
    loss=(-delta.where(delta<0,0)).rolling(14).mean()

    rs=gain/loss
    rsi=float((100-(100/(1+rs))).dropna().iloc[-1])

    trend="UPTREND 📈" if close.iloc[-1]>close.iloc[-20] else "DOWNTREND 📉"
    signal="BUY 🟢" if rsi<30 else "SELL 🔴" if rsi>70 else "HOLD 🟡"

    return {"rsi":round(rsi,2),"trend":trend,"signal":signal}
