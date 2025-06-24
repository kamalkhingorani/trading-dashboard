import yfinance as yf
import pandas as pd
from datetime import datetime

recommendation_tracker = {}

# Initial Recommendation Fetch
def get_us_recos():
    sp500_url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    table = pd.read_html(sp500_url)
    sp500_df = table[0]
    stock_symbols = sp500_df['Symbol'].tolist()

    recommendations = []

    for symbol in stock_symbols:
        try:
            df = yf.download(symbol, period="6mo", interval="1d", progress=False)
            df.dropna(inplace=True)

            df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()
            df["EMA_50"] = df["Close"].ewm(span=50, adjust=False).mean()
            df["EMA_100"] = df["Close"].ewm(span=100, adjust=False).mean()
            df["EMA_200"] = df["Close"].ewm(span=200, adjust=False).mean()

            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))

            latest = df.iloc[-1]
            previous = df.iloc[-2]

            bullish_candle = latest['Close'] > latest['Open']

            if (
                latest["EMA_20"] > latest["EMA_50"]
                and latest["EMA_50"] > latest["EMA_100"]
                and latest["EMA_100"] > latest["EMA_200"]
                and latest["Close"] > latest["EMA_20"]
                and latest["RSI"] > 20
                and bullish_candle
                and latest["Volume"] > previous["Volume"]
            ):
                ltp = round(latest["Close"], 2)
                target = round(ltp * 1.05, 2)
                sl = round(latest["EMA_20"], 2)

                recommendation_tracker[symbol] = {
                    "Date": datetime.now().strftime('%Y-%m-%d'),
                    "Stock": symbol,
                    "LTP": ltp,
                    "Target": target,
                    "% to Target": round(((target - ltp) / ltp) * 100, 2),
                    "Stop Loss": sl,
                    "Remarks": "Active"
                }

                recommendations.append(recommendation_tracker[symbol])

        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

    if recommendations:
        return pd.DataFrame(recommendations)
    else:
        return pd.DataFrame()

# 15-Minute Monitoring Function
def monitor_targets_and_stops():
    for symbol, reco in recommendation_tracker.items():
        if reco["Remarks"] == "Active":
            try:
                df = yf.download(symbol, period="2d", interval="15m", progress=False)
                if not df.empty:
                    current_price = df.iloc[-1]['Close']

                    if current_price >= reco["Target"]:
                        reco["Remarks"] = "Target Achieved"
                    elif current_price <= reco["Stop Loss"]:
                        reco["Remarks"] = "Stop Loss Hit"

            except Exception as e:
                print(f"Error monitoring {symbol}: {e}")

    return pd.DataFrame(list(recommendation_tracker.values()))

# Indian Stock Recommendation and Tracking
indian_recommendation_tracker = {}

indian_stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
                  "LT.NS", "SBIN.NS", "AXISBANK.NS", "MARUTI.NS", "HINDUNILVR.NS"]

# Initial Indian Recommendation Fetch
def get_indian_recos():
    recommendations = []

    for symbol in indian_stocks:
        try:
            df = yf.download(symbol, period="6mo", interval="1d", progress=False)
            df.dropna(inplace=True)

            df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()
            df["EMA_50"] = df["Close"].ewm(span=50, adjust=False).mean()
            df["EMA_100"] = df["Close"].ewm(span=100, adjust=False).mean()
            df["EMA_200"] = df["Close"].ewm(span=200, adjust=False).mean()

            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))

            latest = df.iloc[-1]
            previous = df.iloc[-2]

            bullish_candle = latest['Close'] > latest['Open']

            if (
                latest["EMA_20"] > latest["EMA_50"]
                and latest["EMA_50"] > latest["EMA_100"]
                and latest["EMA_100"] > latest["EMA_200"]
                and latest["Close"] > latest["EMA_20"]
                and latest["RSI"] > 20
                and bullish_candle
                and latest["Volume"] > previous["Volume"]
            ):
                ltp = round(latest["Close"], 2)
                target = round(ltp * 1.05, 2)
                sl = round(latest["EMA_20"], 2)

                indian_recommendation_tracker[symbol] = {
                    "Date": datetime.now().strftime('%Y-%m-%d'),
                    "Stock": symbol,
                    "LTP": ltp,
                    "Target": target,
                    "% to Target": round(((target - ltp) / ltp) * 100, 2),
                    "Stop Loss": sl,
                    "Remarks": "Active"
                }

                recommendations.append(indian_recommendation_tracker[symbol])

        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

    if recommendations:
        return pd.DataFrame(recommendations)
    else:
        return pd.DataFrame()

# 15-Minute Monitoring for Indian Stocks
def monitor_indian_targets_and_stops():
    for symbol, reco in indian_recommendation_tracker.items():
        if reco["Remarks"] == "Active":
            try:
                df = yf.download(symbol, period="2d", interval="15m", progress=False)
                if not df.empty:
                    current_price = df.iloc[-1]['Close']

                    if current_price >= reco["Target"]:
                        reco["Remarks"] = "Target Achieved"
                    elif current_price <= reco["Stop Loss"]:
                        reco["Remarks"] = "Stop Loss Hit"

            except Exception as e:
                print(f"Error monitoring {symbol}: {e}")

    return pd.DataFrame(list(indian_recommendation_tracker.values()))
