import numpy as np

def predict_prices(data):
    close=data["Close"].dropna()
    returns=close.pct_change().dropna()

    avg=returns.mean()
    volatility=returns.std()

    last=close.iloc[-1]

    week=last*(1+avg*5+volatility)
    month=last*(1+avg*22+volatility*2)

    return {
        "week":round(week,2),
        "month":round(month,2)
    }
