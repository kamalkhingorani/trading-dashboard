import streamlit as st

st.set_page_config(page_title="Algo Dashboard", layout="wide")

st.title("Welcome to Kamal's Trading Dashboard (Preview)")
st.markdown("This is a Streamlit version for local testing or Firebase hosting.")
st.info("Coming soon: Live signals, trade tracking, option alerts, and more.")

if st.button("Test Alert"):
    st.success("This is where alerts will appear.")
