import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Kamal's Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
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
    .tab-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2e8b57;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
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

# Embedded Indian Stock Scanner
class SimpleIndianScanner:
    def __init__(self):
        self.symbols = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
            "ICICIBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ASIANPAINT.NS",
            "ITC.NS", "AXISBANK.NS", "LT.NS", "SUNPHARMA.NS", "TITAN.NS"
        ]
    
    def calculate_rsi(self, data, window=14):
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def scan_stocks(self, min_price=25, max_rsi=35):
        recommendations = []
        
        for i, symbol in enumerate(self.symbols[:10]):  # Limit to 10 for demo
            try:
                st.text(f"Scanning {symbol.replace('.NS', '')}...")
                
                stock = yf.Ticker(symbol)
                data = stock.history(period="3mo")
                
                if data.empty:
                    continue
                
                data['RSI'] = self.calculate_rsi(data)
                data['EMA20'] = data['Close'].ewm(span=20).mean()
                data['Volume_MA'] = data['Volume'].rolling(window=20).mean()
                
                latest = data.iloc[-1]
                current_price = latest['Close']
                rsi = latest['RSI']
                
                if current_price >= min_price and rsi <= max_rsi and not pd.isna(rsi):
                    target = current_price * 1.08  # 8% target
                    sl = current_price * 0.94     # 6% SL
                    
                    recommendations.append({
                        'Date': datetime.now().strftime('%Y-%m-%d'),
                        'Stock': symbol.replace('.NS', ''),
                        'LTP': round(current_price, 2),
                        'RSI': round(rsi, 1),
                        'Target': round(target, 2),
                        '% Gain': round(((target - current_price) / current_price) * 100, 1),
                        'Est. Days': 15,
                        'Stop Loss': round(sl, 2),
                        'Remarks': 'Technical setup',
                        'Status': 'Active'
                    })
            except:
                continue
        
        return pd.DataFrame(recommendations)

# Embedded US Stock Scanner
class SimpleUSScanner:
    def __init__(self):
        self.symbols = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM",
            "JNJ", "V", "PG", "UNH", "HD", "MA", "PYPL", "DIS"
        ]
    
    def calculate_rsi(self, data, window=14):
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def scan_stocks(self, min_price=25, max_rsi=35):
        recommendations = []
        
        for i, symbol in enumerate(self.symbols[:10]):
            try:
                st.text(f"Scanning {symbol}...")
                
                stock = yf.Ticker(symbol)
                data = stock.history(period="3mo")
                
                if data.empty:
                    continue
                
                data['RSI'] = self.calculate_rsi(data)
                data['EMA21'] = data['Close'].ewm(span=21).mean()
                
                latest = data.iloc[-1]
                current_price = latest['Close']
                rsi = latest['RSI']
                
                if current_price >= min_price and rsi <= max_rsi and not pd.isna(rsi):
                    target = current_price * 1.06  # 6% target for US
                    sl = current_price * 0.95     # 5% SL
                    
                    recommendations.append({
                        'Date': datetime.now().strftime('%Y-%m-%d'),
                        'Stock': symbol,
                        'LTP': round(current_price, 2),
                        'RSI': round(rsi, 1),
                        'Target': round(target, 2),
                        '% Gain': round(((target - current_price) / current_price) * 100, 1),
                        'Est. Days': 12,
                        'Stop Loss': round(sl, 2),
                        'Remarks': 'US breakout setup',
                        'Status': 'Active'
                    })
            except:
                continue
        
        return pd.DataFrame(recommendations)

# Simple News Function
def get_sample_news():
    return [
        {
            'title': 'RBI Monetary Policy Meeting Today',
            'summary': 'Reserve Bank of India to announce key policy rates. Markets expect status quo on repo rates at 6.5%.',
            'category': 'RBI/Policy',
            'market_impact': 'High',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'title': 'IT Sector Q3 Earnings Begin',
            'summary': 'Major IT companies to report Q3 results this week. Analysts expect strong revenue growth driven by digital transformation deals.',
            'category': 'Corporate Earnings',
            'market_impact': 'Medium',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'title': 'FII Inflows Continue in January',
            'summary': 'Foreign institutional investors pump in $2.1 billion in Indian equities so far this month, boosting market sentiment.',
            'category': 'FII/DII Activity',
            'market_impact': 'Medium',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'title': 'Crude Oil Prices Stable',
            'summary': 'Brent crude trading around $85 per barrel. Stable oil prices positive for Indian economy and markets.',
            'category': 'Commodities',
            'market_impact': 'Low',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]

# Initialize session state
if 'indian_recos' not in st.session_state:
    st.session_state.indian_recos = pd.DataFrame()
if 'us_recos' not in st.session_state:
    st.session_state.us_recos = pd.DataFrame()

# Main title
st.markdown('<h1 class="main-header">📈 Kamal\'s Trading Dashboard</h1>', unsafe_allow_html=True)

# Sidebar controls
st.sidebar.title("Dashboard Controls")
refresh_all = st.sidebar.button("🔄 Refresh All Data")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📰 Live News Feed", 
    "🇮🇳 Indian Stock Recommendations", 
    "🇺🇸 US Stock Recommendations", 
    "📊 Index & Options"
])

# Tab 1: Live News Feed
with tab1:
    st.markdown('<h2 class="tab-header">📰 Live News Feed</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Market Moving News")
        
        if st.button("🔄 Refresh News", key="news_refresh") or refresh_all:
            st.session_state.news_data = get_sample_news()
        
        # Display news
        if 'news_data' in st.session_state:
            for news in st.session_state.news_data:
                with st.container():
                    st.markdown(f"""
                    <div class="news-item">
                        <h4>{news['title']}</h4>
                        <p><strong>Impact:</strong> <span style="color: {'red' if news['market_impact'] == 'High' else 'orange' if news['market_impact'] == 'Medium' else 'green'}">{news['market_impact']}</span> | 
                           <strong>Category:</strong> {news['category']}</p>
                        <p>{news['summary']}</p>
                        <small>⏰ {news['timestamp']}</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            if st.button("Load Sample News"):
                st.session_state.news_data = get_sample_news()
                st.rerun()
    
    with col2:
        st.subheader("Market Overview")
        
        # Market indices
        try:
            nifty_data = yf.download("^NSEI", period="1d")
            if not nifty_data.empty:
                nifty_close = nifty_data['Close'].iloc[-1]
                nifty_open = nifty_data['Open'].iloc[0]
                nifty_change = nifty_close - nifty_open
                st.metric("Nifty 50", f"{nifty_close:.2f}", f"{nifty_change:.2f}")
        except:
            st.metric("Nifty 50", "Loading...", "0.00")
        
        # Market sentiment
        st.subheader("Sentiment")
        sentiment_score = 75  # Sample
        st.progress(sentiment_score / 100)
        st.write(f"Bullish ({sentiment_score}%)")

# Tab 2: Indian Stock Recommendations
with tab2:
    st.markdown('<h2 class="tab-header">🇮🇳 Indian Stock Recommendations</h2>', unsafe_allow_html=True)
    
    # Scanning parameters
    col1, col2, col3 = st.columns(3)
    with col1:
        min_price_in = st.number_input("Min Price (₹)", value=25, min_value=1, key="min_price_in")
    with col2:
        max_rsi_in = st.number_input("Max RSI", value=35, min_value=1, max_value=100, key="max_rsi_in")
    with col3:
        st.write("")  # Spacer
    
    if st.button("🔍 Scan Indian Stocks", key="scan_indian") or refresh_all:
        with st
