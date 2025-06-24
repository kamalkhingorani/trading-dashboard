import yfinance as yf
import pandas as pd
import pandas_ta as ta
import streamlit as st

st.header("Indian Stock Recommendations (Delivery Picks)")

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

            ema20 = latest["EMA_20"]
            ema50 = latest["EMA_50"]
            ema100 = latest["EMA_100"]
            ema200 = latest["EMA_200"]
            close = latest["Close"]
            rsi = latest["RSI"]
            volume = latest["Volume"]
            prev_volume = previous["Volume"]

            # Bullish candle check: close > open
            bullish_candle = latest["Close"] > latest["Open"]

            if (
                (ema20 > ema50 > ema100 > ema200) and
                (close > ema20) and
                (rsi > 20) and
                bullish_candle and
                (volume > prev_volume)
            ):
                recommendations.append({
                    "Stock": symbol.replace(".NS", ""),
                    "Price": round(close, 2),
                    "EMA 20": round(ema20, 2),
                    "EMA 50": round(ema50, 2),
                    "EMA 100": round(ema100, 2),
                    "EMA 200": round(ema200, 2),
                    "RSI": round(rsi, 2),
                    "Volume": int(volume)
                })

        except Exception as e:
            st.warning(f"Error fetching data for {symbol}: {e}")

    if recommendations:
        df_result = pd.DataFrame(recommendations)
        st.dataframe(df_result, use_container_width=True)
    else:
        st.info("No bullish stock setups matching criteria were found today.")
