import pandas as pd
import requests

def get_indian_recos():
    # Placeholder logic: fetch from a free screener or mock
    data = [
        {"Symbol": "RELIANCE", "Date": "2025-06-16", "Price": 2600, "Target": 2730,
         "SL": 2550, "Reason": "Bullish breakout", "Status": "Open"},
        {"Symbol": "TCS", "Date": "2025-06-16", "Price": 3300, "Target": 3465,
         "SL": 3200, "Reason": "Earnings volume spike", "Status": "Open"},
    ]
    return pd.DataFrame(data)

def get_us_recos():
    api_key = "demo"
    url = f"https://financialmodelingprep.com/api/v3/stock/real-time-price/AAPL?apikey={api_key}"
    resp = requests.get(url).json()
    data = [
        {"Symbol": resp["symbol"], "Price": resp["price"], "Target": resp["price"]*1.05,
         "SL": resp["price"]*0.97, "Reason": "Momentum breakout", "Date": pd.Timestamp.now()},
    ]
    return pd.DataFrame(data)
