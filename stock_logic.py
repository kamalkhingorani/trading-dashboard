import pandas as pd
import requests

def get_indian_recos():
    data = [
        {"Symbol":"RELIANCE", "Date":"2025-06-16", "Price":2600, "Target":2730, "SL":2550, "Reason":"Bullish breakout", "Status":"Open"},
        {"Symbol":"TCS", "Date":"2025-06-16", "Price":3300, "Target":3465, "SL":3200, "Reason":"Earnings volume spike", "Status":"Open"},
    ]
    return pd.DataFrame(data)

def get_us_recos():
    api_key = "demo"  # swap in your own key
    symbol = "AAPL"
    url = f"https://financialmodelingprep.com/api/v3/quote-short/{symbol}?apikey={api_key}"
    resp = requests.get(url).json()

    if not resp or not isinstance(resp, list):
        # fallback or empty
        return pd.DataFrame([{"Symbol": symbol, "Price": None, "Target": None, "SL": None, "Reason": "API error", "Date": pd.Timestamp.now()}])

    item = resp[0]
    price = item.get("price")
    if price is None:
        return pd.DataFrame([{"Symbol": symbol, "Price": None, "Target": None, "SL": None, "Reason": "Missing price", "Date": pd.Timestamp.now()}])

    target = round(price * 1.05, 2)
    sl = round(price * 0.97, 2)
    pct = round(((target - price) / price) * 100, 2)
    days_est = 5  # example estimate

    data = [{
        "Symbol": item.get("symbol", symbol),
        "Date": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "Price": price,
        "Target": target,
        "SL": sl,
        "% Rise": pct,
        "Est Days": days_est,
        "Reason": "Momentum breakout",
        "Status": "Open"
    }]
    return pd.DataFrame(data)
