import streamlit as st
from stock_logic import get_indian_recos, get_us_recos
from news_logic import fetch_live_news

st.set_page_config(page_title="Trading Dashboard", layout="wide")
tabs = st.tabs(["📰 Live News", "🇮🇳 Indian Stocks", "🇺🇸 US Stocks", "📈 Index & Options"])

with tabs[0]:
    st.header("Live News")
    news = fetch_live_news()
    seen = set()
    for item in news:
        if item['title'] not in seen:
            st.markdown(f"- [{item['title']}]({item['link']})")
            seen.add(item['title'])

with tabs[1]:
    st.header("Indian Stock Recommendations")
    df = get_indian_recos()
    st.dataframe(df)

with tabs[2]:
    st.header("US Stock Recommendations")
    df_us = get_us_recos()
    st.dataframe(df_us)

with tabs[3]:
    st.header("Index & Options Recommendations")
    st.write("Coming soon—integrating Dhan option signals here.")
