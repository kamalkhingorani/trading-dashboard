import requests

def get_latest_news():
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": "1ceb6cfbbbc54ed9b39bc27801c9b04c",
        "country": "in",
        "pageSize": 10
    }
    resp = requests.get(url, params=params).json()
    return [{"title": a["title"], "link": a["url"]} for a in resp.get("articles", [])]
