import pandas as pd

def get_recommendations():
    data = {
        "Recommendation Date": ["2025-06-03"],
        "Stock": ["ABC Ltd"],
        "Entry Price": [120],
        "Target Price": [134.5],
        "% Return": ["+12.1%"],
        "Stop Loss": [112],
        "Target Date": ["2025-06-07"],
        "Days to Target": [4],
        "Signal Type": ["EMA + Breakout"],
        "Status": ["Target Hit"],
        "News Link": ["https://news.example.com/abc"]
    }
    return pd.DataFrame(data)