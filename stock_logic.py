
import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.header("📈 Indian Stock Recommendations (Delivery Picks)")


# Define the stock symbols (NSE stocks with Yahoo-compatible tickers)
def get_indian_recos():
stock_symbols = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "LT.NS", "SBIN.NS", "AXISBANK.NS", "MARUTI.NS", "HINDUNILVR.NS"
]

recommendations = []

for symbol in stock_symbols:
    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)
        df.dropna(inplace=True)
        df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()
        df["EMA_50"] = df["Close"].ewm(span=50, adjust=False).mean()
        df["EMA_100"] = df["Close"].ewm(span=100, adjust=False).mean()
        df["EMA_200"] = df["Close"].ewm(span=200, adjust=False).mean()
        df["RSI"] = ta.momentum.RSIIndicator(df["Close"], window=14).rsi()

        latest = df.iloc[-1]
        previous = df.iloc[-2]

        # Criteria: EMAs aligned bullish, price > EMA_20, RSI between 40–70, increasing volume
        if (
            latest["EMA_20"] > latest["EMA_50"] > latest["EMA_100"] > latest["EMA_200"] and
            latest["Close"] > latest["EMA_20"] and
            40 < latest["RSI"] < 70 and
            latest["Volume"] > previous["Volume"]
        ):
            recommendations.append({
                "Stock": symbol.replace(".NS", ""),
                "Price": round(latest["Close"], 2),
                "EMA 20": round(latest["EMA_20"], 2),
                "EMA 50": round(latest["EMA_50"], 2),
                "EMA 100": round(latest["EMA_100"], 2),
                "EMA 200": round(latest["EMA_200"], 2),
                "RSI": round(latest["RSI"], 2),
                "Volume": int(latest["Volume"])
            })
    except Exception as e:
        st.warning(f"Error fetching data for {symbol}: {e}")

if recommendations:
    df_result = pd.DataFrame(recommendations)
    st.dataframe(df_result, use_container_width=True)
else:
    st.info("No bullish stock setups matching criteria were found today.")
