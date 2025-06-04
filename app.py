import streamlit as st
from stock_logic import get_recommendations
from news_logic import get_latest_news

st.set_page_config(page_title="Kamal's Trading Dashboard", layout="wide")

# Sidebar or Header
st.title("📊 Kamal's Trading Dashboard")

# Tabs
tabs = st.tabs(["📢 Live News Feed", "📈 Indian Stock Recommendations", "🧠 Manual Trade Controls (Coming Soon)"])

# News Tab
with tabs[0]:
    st.header("Live News Feed")
    news = get_latest_news()
    if news:
        for item in news:
            st.markdown(f"- [{item['title']}]({item['link']})")
    else:
        st.info("No news items found.")

# Stock Recommendations Tab
with tabs[1]:
    st.header("Indian Stock Recommendations")
    df = get_recommendations()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No matching stock recommendations today.")

# Manual Trade Controls Placeholder
with tabs[2]:
    st.info("This section will include manual trade buttons, capital override, partial liquidation controls, and spike entries. Coming in GCP deployment.")