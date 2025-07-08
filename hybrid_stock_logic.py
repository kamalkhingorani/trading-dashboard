import yfinance as yf
import pandas as pd
from datetime import datetime

# --- Trackers ---
us_reco_tracker = {}
indian_reco_tracker = {}

# --- US Stock Recommendation ---
def get_us_recos():
    sp500_url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    try:
        table = pd.read_html(sp500_url)
        sp500_df = table[0]
        stock_symbols = sp500_df['Symbol'].tolist()
    except Exception as e:
        print(f"Error fetching S&P 500 symbols: {e}")
        return pd.DataFrame()

    recommendations = []

    for symbol in stock_symbols:
        try:
            df = yf.download(symbol, period="6mo", interval="1d", progress=False)
            df.dropna(inplace=True)

            df["EMA_20"] = df["Close"].ewm(span=20).mean()
            df["EMA_50"] = df["Close"].ewm(span=50).mean()
            df["EMA_100"] = df["Close"].ewm(span=100).mean()
            df["EMA_200"] = df["Close"].ewm(span=200).mean()

            delta = df['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(window=14).mean()
            loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
            rs = gain / loss
            df["RSI"] = 100 - (100 / (1 + rs))

            latest = df.iloc[-1]
            previous = df.iloc[-2]

            if (
                latest["RSI"] > 20 and
                latest["Close"] > latest["Open"] and
                latest["Volume"] > previous["Volume"]
            ):
                ltp = round(latest["Close"], 2)
                target = round(ltp * 1.05, 2)
                sl = round(min(latest["Low"], latest["EMA_20"], latest["EMA_50"]), 2)

                reco = {
                    "Date": datetime.now().strftime('%Y-%m-%d'),
                    "Stock": symbol,
                    "Price": ltp,
                    "Target": target,
                    "Stop Loss": sl,
                    "% to Target": round(((target - ltp) / ltp) * 100, 2),
                    "Status": "Active",
                }

                us_reco_tracker[symbol] = reco
                recommendations.append(reco)

        except Exception as e:
            print(f"Error with US stock {symbol}: {e}")

    return pd.DataFrame(recommendations)

# --- Indian Stock Recommendation ---
def get_indian_recos():
    try:
        nse100 = [
            "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "LT.NS",
            "SBIN.NS", "AXISBANK.NS", "MARUTI.NS", "HINDUNILVR.NS", "ITC.NS", "WIPRO.NS",
            "BHARTIARTL.NS", "KOTAKBANK.NS", "SUNPHARMA.NS", "HCLTECH.NS", "BAJFINANCE.NS",
            "ADANIENT.NS", "ULTRACEMCO.NS", "ASIANPAINT.NS", "DMART.NS", "BAJAJFINSV.NS"
        ]
    except Exception as e:
        print(f"Error defining stock universe: {e}")
        return pd.DataFrame()

    recommendations = []

    for symbol in nse100:
        try:
            df = yf.download(symbol, period="6mo", interval="1d", progress=False)
            df.dropna(inplace=True)

            if df["Close"].iloc[-1] < 25:
                continue

            df["EMA_20"] = df["Close"].ewm(span=20).mean()
            df["EMA_50"] = df["Close"].ewm(span=50).mean()
            df["EMA_100"] = df["Close"].ewm(span=100).mean()
            df["EMA_200"] = df["Close"].ewm(span=200).mean()

            delta = df['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(window=14).mean()
            loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
            rs = gain / loss
            df["RSI"] = 100 - (100 / (1 + rs))

            latest = df.iloc[-1]
            previous = df.iloc[-2]

            if (
                latest["RSI"] > 20 and
                latest["Close"] > latest["Open"] and
                latest["Volume"] > previous["Volume"]
            ):
                ltp = round(latest["Close"], 2)
                target = round(ltp * 1.05, 2)
                sl = round(min(latest["Low"], latest["EMA_20"], latest["EMA_50"]), 2)

                reco = {
                    "Date": datetime.now().strftime('%Y-%m-%d'),
                    "Stock": symbol.replace(".NS", ""),
                    "Price": ltp,
                    "Target": target,
                    "Stop Loss": sl,
                    "% to Target": round(((target - ltp) / ltp) * 100, 2),
                    "Status": "Active",
                }

                indian_reco_tracker[symbol] = reco
                recommendations.append(reco)

        except Exception as e:
            print(f"Error with Indian stock {symbol}:

            return pd.DataFrame(recommendations)
