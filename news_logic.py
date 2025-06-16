import requests

def fetch_live_news():
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": "YOUR_NEWSAPI_KEY",
        "country": "in",
        "pageSize": 10
    }
    resp = requests.get(url, params=params).json()
    return [{"title": a["title"], "link": a["url"]} for a in resp.get("articles", [])]
