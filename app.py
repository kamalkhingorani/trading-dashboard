
import streamlit as st
from news_logic import get_latest_news
from hybrid_stock_logic import get_indian_recos, get_us_recos

st.set_page_config(page_title="Kamal's Trading Dashboard", layout="wide")
st.title("📊 Kamal's Trading Dashboard")

tabs = st.tabs(["📰 Live News Feed", "🇮🇳 Indian Stock Recommendations", "🇺🇸 US Stock Recommendations", "📈 Index & Options"])

with tabs[0]:
    st.header("Live News Feed")
    news_items = get_latest_news()
    if news_items:
        for item in news_items:
            st.markdown(f"- [{item['title']}]({item['link']})")
    else:
        st.info("No items found.")

with tabs[1]:
    st.header("IN Stock Recommendations")
    indian_recos = get_indian_recos()
    st.write("Total Indian recommendations found:", len(indian_recos))
    if indian_recos:
        st.dataframe(indian_recos)
    else:
        st.warning("No Indian stock recommendations available.")

with tabs[2]:
    st.header("US Stock Recommendations")
    us_recos = get_us_recos()
    st.write("Total US recommendations found:", len(us_recos))
    if us_recos:
        st.dataframe(us_recos)
    else:
        st.warning("No US stock recommendations available.")

with tabs[3]:
    st.header("Index & Options")
    st.info("This section will be updated soon.")
