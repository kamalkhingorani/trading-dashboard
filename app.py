
import streamlit as st
import requests
import datetime

st.set_page_config(page_title="Kamal's Trading Dashboard", layout="wide")

# Sidebar Navigation
tabs = st.sidebar.radio("Navigation", ["Home", "Live Market News"])

# Home Tab
if tabs == "Home":
    st.title("Welcome to Kamal's Trading Dashboard (Preview)")
    st.markdown("This is a Streamlit version for local testing or Firebase hosting.")
    st.info("Coming soon: Live signals, trade tracking, option alerts, and more.")
    if st.button("Test Alert"):
        st.success("This is where alerts will appear.")

# News Tab
if tabs == "Live Market News":
    st.title("Live Market News")

    # Sample free news API (limited demo) - replace with your own API key if needed
    url = "https://newsdata.io/api/1/news?apikey=pub_cf4970ef7dde4d21a2f35680faf7d764&q=finance,stock,india,global&language=en"

    try:
        response = requests.get(url)
        data = response.json()
        articles = data.get("results", [])

        for article in articles[:10]:
            title = article.get("title", "No title")
            pub_date = article.get("pubDate", "No date")
            link = article.get("link", "#")
            source = article.get("source_id", "Unknown")

            st.markdown(f"**{title}**")
            st.markdown(f"*Source: {source} | Published: {pub_date}*")
            st.markdown(f"[Read more]({link})")
            st.markdown("---")
    except Exception as e:
        st.error("Failed to load news. Please check your API or internet connection.")
