
import yfinance as yf
import pandas as pd
import datetime
import streamlit as st

def get_indian_recos():
    symbols = pd.read_csv("https://archives.nseindia.com/content/indices/ind_nifty500list.csv")["Symbol"].tolist()
    indian_recos = []
    print("Total stocks being checked (India):", len(symbols))
    for symbol in symbols:
        symbol_ns = symbol + ".NS"
        try:
            data = yf.download(symbol_ns, period="6mo", interval="1d", progress=False)
            if data.empty:
                print("No data for", symbol)
                continue
            close_price = data["Close"].iloc[-1]
            if close_price < 25:  # for Indian stocks
                continue
            data["EMA20"] = data["Close"].ewm(span=20).mean()
            data["EMA50"] = data["Close"].ewm(span=50).mean()
            data["EMA100"] = data["Close"].ewm(span=100).mean()
            data["EMA200"] = data["Close"].ewm(span=200).mean()

            if (
                data["EMA20"].iloc[-1] > data["EMA50"].iloc[-1] > data["EMA100"].iloc[-1] > data["EMA200"].iloc[-1] and
                close_price > data["EMA20"].iloc[-1]
            ):
                target = round(close_price * 1.05, 2)
                sl = round(data["EMA50"].iloc[-1], 2)
                reco = {
                    "Date": datetime.date.today(),
                    "Stock": symbol,
                    "Close": round(close_price, 2),
                    "EMA20": round(data["EMA20"].iloc[-1], 2),
                    "EMA50": round(data["EMA50"].iloc[-1], 2),
                    "Target": target,
                    "Stop Loss": sl,
                    "% Return": round((target - close_price) / close_price * 100, 2)
                }
                indian_recos.append(reco)
                print("Reco generated for", symbol)
            else:
                print("Skipped", symbol)
        except Exception as e:
            print(f"Error with {symbol}: {e}")
    return indian_recos


def get_us_recos():
    sp500 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
    symbols = sp500["Symbol"].tolist()
    us_recos = []
    print("Total stocks being checked (US):", len(symbols))
    for symbol in symbols:
        try:
            data = yf.download(symbol, period="6mo", interval="1d", progress=False)
            if data.empty:
                print("No data for", symbol)
                continue
            close_price = data["Close"].iloc[-1]
            data["EMA20"] = data["Close"].ewm(span=20).mean()
            data["EMA50"] = data["Close"].ewm(span=50).mean()
            data["EMA100"] = data["Close"].ewm(span=100).mean()
            data["EMA200"] = data["Close"].ewm(span=200).mean()

            if (
                data["EMA20"].iloc[-1] > data["EMA50"].iloc[-1] > data["EMA100"].iloc[-1] > data["EMA200"].iloc[-1] and
                close_price > data["EMA20"].iloc[-1]
            ):
                target = round(close_price * 1.05, 2)
                sl = round(data["EMA50"].iloc[-1], 2)
                reco = {
                    "Date": datetime.date.today(),
                    "Stock": symbol,
                    "Close": round(close_price, 2),
                    "EMA20": round(data["EMA20"].iloc[-1], 2),
                    "EMA50": round(data["EMA50"].iloc[-1], 2),
                    "Target": target,
                    "Stop Loss": sl,
                    "% Return": round((target - close_price) / close_price * 100, 2)
                }
                us_recos.append(reco)
                print("Reco generated for", symbol)
            else:
                print("Skipped", symbol)
        except Exception as e:
            print(f"Error with {symbol}: {e}")
    return us_recos
