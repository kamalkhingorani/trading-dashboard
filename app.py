# app.py
import streamlit as st
from stock_logic import get_indian_recos
from news_logic import get_latest_news
from US_stock_logic import get_us_recos

st.set_page_config(page_title="Kamal's Trading Dashboard", layout="wide")

st.title("📊 Kamal's Trading Dashboard")

tabs = st.tabs(["📰 Live News Feed", "🇮🇳 Indian Stock Recommendations", "🇺🇸 US Stock Recommendations", "📈 Index & Options"])

# News Tab
with tabs[0]:
    st.header("Live News Feed")
    news = get_latest_news()
    if news:
        for item in news:
            st.markdown(f"- [{item['title']}]({item['link']})")
    else:
        st.info("No items found.")

# Indian Stocks Tab
with tabs[1]:
    st.header("IN Stock Recommendations")
    df_in = get_indian_recos()
    
    if df_in is not None and not df_in.empty:
        df_in["% to Target"] = ((df_in["Target"] - df_in["Price"]) / df_in["Price"] * 100).round(2)
        df_in["Est. Days to Target"] = df_in["% to Target"].apply(lambda x: max(1, int(x/1.5)))
        st.dataframe(df_in)
    else:
        st.warning("No Indian stock recommendations available.")

# US Stocks Tab
with tabs[2]:
    st.header("US Stock Recommendations")
    df_us = get_us_recos()
    if df_us is not None and not df_us.empty:
        try:
            df_us["% to Target"] = ((df_us["Target"] - df_us["Price"]) / df_us["Price"] * 100).round(2)
            df_us["Est. Days to Target"] = df_us["% to Target"].apply(lambda x: max(1, int(x/1.5)))
            st.dataframe(df_us)
        except KeyError as e:
            st.error(f"Missing column: {e}")
    else:
        st.warning("No US stock recommendations available.")

# Index Tab
with tabs[3]:
    st.header("Index & Options")
    st.info("Coming soon. Contact Kamal for advanced deployment access.")
