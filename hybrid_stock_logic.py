import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit as st

recommendation_tracker = {}
indian_recommendation_tracker = {}

# ----------- Fetch NIFTY 500 Symbols (NSE) -----------
def get_nse500_symbols():
    url = "https://en.wikipedia.org/wiki/NIFTY_500"
    try:
        tables = pd.read_html(url)
        df = tables[1] if len(tables) > 1 else tables[0]
        df['Symbol'] = df['Company Name'].str.extract(r'(\w+)\s*\(')[0] + ".NS"
        return df['Symbol'].dropna().unique().tolist()
    except Exception as e:
        print("Error fetching NSE500 list:", e)
        return []

# ----------- Filter Stocks Above ₹25 -----------
def filter_symbols_above_25(symbols):
    filtered = []
    for symbol in symbols:
        try:
            data = yf.download(symbol, period="1d", interval="1d", progress=False)
            if not data.empty and data["Close"].iloc[-1] > 25:
                filtered.append(symbol)
        except:
            continue
    return filtered

# ----------- Indian Stock Recommendations -----------
def get_indian_recos():
    symbols = filter_symbols_above_25(get_nse500_symbols())
    recommendations = []

    for symbol in symbols:
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
                latest["RSI"] > 20
                and bullish_candle
                and latest["Volume"] > previous["Volume"]
            ):
                ltp = round(latest["Close"], 2)
                target = round(ltp * 1.05, 2)
                sl = round(min(latest["EMA_50"], latest["EMA_100"]), 2)

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

# ----------- US Stock Recommendations -----------
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
                latest["RSI"] > 20
                and bullish_candle
                and latest["Volume"] > previous["Volume"]
            ):
                ltp = round(latest["Close"], 2)
                target = round(ltp * 1.05, 2)
                sl = round(min(latest["EMA_50"], latest["EMA_100"]), 2)

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
