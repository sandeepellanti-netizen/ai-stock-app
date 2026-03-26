
def predict_lightweight(df):
    last = df['Close'].iloc[-1]
    return {
        "1_week": round(last * 1.02, 2),
        "1_month": round(last * 1.05, 2)
    }
