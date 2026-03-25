import requests

NEWS_API_KEY = "a0ffc5cef7fc4ea58edae0d50e263f2b"

def get_news_sentiment(symbol):
    url=f"https://newsapi.org/v2/everything?q={symbol}&apiKey={NEWS_API_KEY}"
    res=requests.get(url).json()

    articles=res.get("articles",[])[:5]

    score=0
    headlines=[]

    for a in articles:
        title=a["title"]
        headlines.append(title)
        t=title.lower()

        if any(w in t for w in ["gain","profit","up"]):
            score+=1
        if any(w in t for w in ["loss","down","fall"]):
            score-=1

    sentiment="Positive 🟢" if score>0 else "Negative 🔴" if score<0 else "Neutral 🟡"

    return {"sentiment":sentiment,"headlines":headlines}
