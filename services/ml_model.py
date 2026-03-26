def predict_lightweight(price):
    # Simple ML-like logic
    pred_week = price * 1.02
    pred_month = price * 1.05
    return pred_week, pred_month
