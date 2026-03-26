
import requests

NEWS_API_KEY = "a0ffc5cef7fc4ea58edae0d50e263f2b"

def get_news(symbol):
    try:
        url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey={NEWS_API_KEY}"
        res = requests.get(url).json()
        return [{"title": a["title"], "url": a["url"]} for a in res.get("articles", [])[:5]]
    except:
        return []

def analyze_sentiment(news):
    text = " ".join([n["title"] for n in news]).lower()
    pos = ["gain","rise","profit"]
    neg = ["fall","loss","drop"]
    score = sum(w in text for w in pos) - sum(w in text for w in neg)
    return "Positive" if score>0 else "Negative" if score<0 else "Neutral"
