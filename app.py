import requests

NEWS_API_KEY = "YOUR_NEWS_API_KEY"  # optional

def get_news(symbol):
    try:
        url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey={NEWS_API_KEY}"
        response = requests.get(url).json()

        articles = []
        for article in response.get("articles", [])[:5]:
            articles.append({
                "title": article["title"],
                "url": article["url"]
            })

        return articles

    except Exception:
        return []

def analyze_sentiment(news_list):
    if not news_list:
        return "Neutral"

    text = " ".join([n["title"] for n in news_list]).lower()

    positive_words = ["gain", "bull", "rise", "profit", "growth"]
    negative_words = ["fall", "bear", "loss", "drop", "decline"]

    score = 0

    for word in positive_words:
        if word in text:
            score += 1

    for word in negative_words:
        if word in text:
            score -= 1

    if score > 0:
        return "Positive"
    elif score < 0:
        return "Negative"
    else:
        return "Neutral"
