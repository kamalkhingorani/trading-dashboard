import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Kamal's Trading Dashboard",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .news-item {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Simple scanners
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def scan_indian_stocks(min_price=25, max_rsi=35):
    symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"]
    recommendations = []
    
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period="3mo")
            
            if data.empty:
                continue
                
            data['RSI'] = calculate_rsi(data)
            latest = data.iloc[-1]
            current_price = latest['Close']
            rsi = latest['RSI']
            
            if current_price >= min_price and rsi <= max_rsi and not pd.isna(rsi):
                target = current_price * 1.08
                sl = current_price * 0.94
                
                recommendations.append({
                    'Date': datetime.now().strftime('%Y-%m-%d'),
                    'Stock': symbol.replace('.NS', ''),
                    'LTP': round(current_price, 2),
                    'RSI': round(rsi, 1),
                    'Target': round(target, 2),
                    '% Gain': round(((target - current_price) / current_price) * 100, 1),
                    'Stop Loss': round(sl, 2),
                    'Status': 'Active'
                })
        except:
            continue
    
    return pd.DataFrame(recommendations)

def scan_us_stocks(min_price=25, max_rsi=35):
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    recommendations = []
    
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period="3mo")
            
            if data.empty:
                continue
                
            data['RSI'] = calculate_rsi(data)
            latest = data.iloc[-1]
            current_price = latest['Close']
            rsi = latest['RSI']
            
            if current_price >= min_price and rsi <= max_rsi and not pd.isna(rsi):
                target = current_price * 1.06
                sl = current_price * 0.95
                
                recommendations.append({
                    'Date': datetime.now().strftime('%Y-%m-%d'),
                    'Stock': symbol,
                    'LTP': round(current_price, 2),
                    'RSI': round(rsi, 1),
                    'Target': round(target, 2),
                    '% Gain': round(((target - current_price) / current_price) * 100, 1),
                    'Stop Loss': round(sl, 2),
                    'Status': 'Active'
                })
        except:
            continue
    
    return pd.DataFrame(recommendations)

def get_sample_news():
    return [
        {
            'title': 'RBI Monetary Policy Meeting Today',
            'summary': 'Reserve Bank of India to announce key policy rates. Markets expect status quo on repo rates.',
            'category': 'RBI/Policy',
            'market_impact': 'High'
        },
        {
            'title': 'IT Sector Q3 Earnings Begin',
            'summary': 'Major IT companies to report Q3 results this week. Strong growth expected.',
            'category': 'Corporate Earnings',
            'market_impact': 'Medium'
        }
    ]

# Initialize session state
if 'indian_recos' not in st.session_state:
    st.session_state.indian_recos = pd.DataFrame()
if 'us_recos' not in st.session_state:
    st.session_state.us_recos = pd.DataFrame()
if 'news_data' not in st.session_state:
    st.session_state.news_data = get_sample_news()

# Main title
st.markdown('<h1 class="main-header">📈 Kamal\'s Trading Dashboard</h1>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📰 Live News Feed", 
    "🇮🇳 Indian Stock Recommendations", 
    "🇺🇸 US Stock Recommendations", 
    "📊 Index & Options"
])

# Tab 1: Live News Feed
with tab1:
    st.subheader("📰 Market Moving News")
    
    if st.button("🔄 Refresh News"):
        st.session_state.news_data = get_sample_news()
        st.success("News refreshed!")
    
    for news in st.session_state.news_data:
        with st.container():
            st.markdown(f"""
            <div class="news-item">
                <h4>{news['title']}</h4>
                <p><strong>Impact:</strong> {news['market_impact']} | <strong>Category:</strong> {news['category']}</p>
                <p>{news['summary']}</p>
            </div>
            """, unsafe_allow_html=True)

# Tab 2: Indian Stock Recommendations
with tab2:
    st.subheader("🇮🇳 Indian Stock Recommendations")
    
    col1, col2 = st.columns(2)
    with col1:
        min_price_in = st.number_input("Min Price (₹)", value=25, min_value=1)
    with col2:
        max_rsi_in = st.number_input("Max RSI", value=35, min_value=1, max_value=100)
    
    if st.button("🔍 Scan Indian Stocks"):
        with st.spinner("Scanning Indian stocks..."):
            st.session_state.indian_recos = scan_indian_stocks(min_price_in, max_rsi_in)
            if not st.session_state.indian_recos.empty:
                st.success(f"Found {len(st.session_state.indian_recos)} recommendations!")
            else:
                st.info("No stocks found matching criteria")
    
    if not st.session_state.indian_recos.empty:
        st.dataframe(st.session_state.indian_recos, use_container_width=True)
    else:
        st.info("Click 'Scan Indian Stocks' to generate recommendations")

# Tab 3: US Stock Recommendations
with tab3:
    st.subheader("🇺🇸 US Stock Recommendations")
    
    col1, col2 = st.columns(2)
    with col1:
        min_price_us = st.number_input("Min Price ($)", value=25, min_value=1)
    with col2:
        max_rsi_us = st.number_input("Max RSI (US)", value=35, min_value=1, max_value=100)
    
    if st.button("🔍 Scan US Stocks"):
        with st.spinner("Scanning US stocks..."):
            st.session_state.us_recos = scan_us_stocks(min_price_us, max_rsi_us)
            if not st.session_state.us_recos.empty:
                st.success(f"Found {len(st.session_state.us_recos)} recommendations!")
            else:
                st.info("No stocks found matching criteria")
    
    if not st.session_state.us_recos.empty:
        st.dataframe(st.session_state.us_recos, use_container_width=True)
    else:
        st.info("Click 'Scan US Stocks' to generate recommendations")

# Tab 4: Index & Options
with tab4:
    st.subheader("📊 Index & Options")
    
    subtab1, subtab2 = st.tabs(["F&O Recommendations", "Algorithm Controls"])
    
    with subtab1:
        st.subheader("F&O Opportunities")
        
        # Sample F&O data
        sample_fno = pd.DataFrame({
            'Symbol': ['NIFTY', 'BANKNIFTY'],
            'Strike': [22000, 48000],
            'Type': ['CE', 'PE'],
            'LTP': [150.50, 200.75],
            'Target': [200.00, 250.00],
            '% Gain': [32.8, 24.6],
            'Remarks': ['Bullish breakout', 'Support bounce']
        })
        st.dataframe(sample_fno, use_container_width=True)
    
    with subtab2:
        st.subheader("🤖 Algorithm Controls")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Status", "⏸️ Stopped")
        with col2:
            st.metric("Positions", "0")
        with col3:
            st.metric("P&L", "₹0")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Start Algorithm", type="primary"):
                st.success("Algorithm started!")
        with col2:
            if st.button("⏹️ Stop Algorithm"):
                st.error("Algorithm stopped!")

# Footer
st.markdown("---")
st.markdown(f"© 2025 Trading Dashboard | Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
