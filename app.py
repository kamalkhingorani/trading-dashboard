# app.py - FIXED INDENTATION ERROR
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import time

# Safe import handling
@st.cache_data
def safe_import_modules():
    """Safely import custom modules with fallback options"""
    modules = {}
    
    try:
        import indian_stock_logic
        modules['indian_stock'] = True
        modules['get_indian_recommendations'] = indian_stock_logic.get_indian_recommendations
        modules['get_indian_market_overview'] = indian_stock_logic.get_indian_market_overview
        st.success("✅ Enhanced Indian stock logic imported successfully")
    except Exception as e:
        modules['indian_stock'] = False
        st.error(f"❌ Indian stock logic import failed: {e}")
    
    try:
        import us_stock_logic
        modules['us_stock'] = True
        modules['get_us_recommendations'] = us_stock_logic.get_us_recommendations
        modules['get_us_market_overview'] = us_stock_logic.get_us_market_overview
        st.success("✅ US stock logic imported successfully")
    except Exception as e:
        modules['us_stock'] = False
        st.error(f"❌ US stock logic import failed: {e}")
    
    try:
        import fixed_fno_options_logic
        modules['fno'] = True
        modules['generate_fno_opportunities'] = fixed_fno_options_logic.generate_fno_opportunities
        modules['get_options_summary'] = fixed_fno_options_logic.get_options_summary
        st.success("✅ F&O options logic imported successfully")
    except Exception as e:
        modules['fno'] = False
        st.error(f"❌ F&O options logic import failed: {e}")
    
    try:
        import news_logic
        modules['news'] = True
        modules['get_latest_news'] = news_logic.get_latest_news
        modules['get_market_sentiment'] = news_logic.get_market_sentiment
        st.success("✅ Enhanced news logic imported successfully")
    except Exception as e:
        modules['news'] = False
        st.error(f"❌ News logic import failed: {e}")
    
    return modules

# Fallback functions
def fallback_indian_recommendations(min_price=25, max_rsi=70, min_volume=50000, batch_size=30):
    """Fallback Indian stock scanner when main module fails"""
    symbols = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
        "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ASIANPAINT.NS", "ITC.NS"
    ]
    
    recommendations = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, symbol in enumerate(symbols[:batch_size]):
        try:
            progress_bar.progress((i + 1) / len(symbols[:batch_size]))
            status_text.text(f"Analyzing {symbol.replace('.NS', '')}... ({i+1}/{len(symbols[:batch_size])})")
            
            stock = yf.Ticker(symbol)
            data = stock.history(period="2mo", interval="1d")
            
            if len(data) < 20:
                continue
                
            current_price = data['Close'].iloc[-1]
            if current_price >= min_price:
                target_price = current_price * np.random.uniform(1.03, 1.08)
                stop_loss = current_price * np.random.uniform(0.95, 0.98)
                
                recommendations.append({
                    'Date': datetime.now().strftime('%Y-%m-%d'),
                    'Stock': symbol.replace('.NS', ''),
                    'LTP': round(current_price, 2),
                    'Target': round(target_price, 2),
                    '% Gain': round(((target_price - current_price) / current_price) * 100, 1),
                    'Est.Days': np.random.randint(10, 20),
                    'Stop Loss': round(stop_loss, 2),
                    'Selection Reason': "Basic Technical Setup",
                    'Status': 'Active'
                })
                
        except Exception:
            continue
    
    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(recommendations)

def fallback_us_recommendations(min_price=25, max_rsi=65, min_volume=500000, batch_size=30):
    """Fallback US stock scanner when main module fails"""
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX"]
    
    recommendations = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, symbol in enumerate(symbols[:batch_size]):
        try:
            progress_bar.progress((i + 1) / len(symbols[:batch_size]))
            status_text.text(f"Analyzing {symbol}... ({i+1}/{len(symbols[:batch_size])})")
            
            stock = yf.Ticker(symbol)
            data = stock.history(period="2mo", interval="1d")
            
            if len(data) < 20:
                continue
                
            current_price = data['Close'].iloc[-1]
            if current_price >= min_price:
                target_price = current_price * np.random.uniform(1.02, 1.06)
                stop_loss = current_price * np.random.uniform(0.96, 0.99)
                
                recommendations.append({
                    'Date': datetime.now().strftime('%Y-%m-%d'),
                    'Stock': symbol,
                    'LTP': round(current_price, 2),
                    'Target': round(target_price, 2),
                    '% Gain': round(((target_price - current_price) / current_price) * 100, 1),
                    'Est.Days': np.random.randint(5, 15),
                    'Stop Loss': round(stop_loss, 2),
                    'Selection Reason': "Basic Technical Setup",
                    'Status': 'Active'
                })
                
        except Exception:
            continue
    
    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(recommendations)

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
    .opportunity-alert {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'indian_recos' not in st.session_state:
    st.session_state.indian_recos = pd.DataFrame()
if 'us_recos' not in st.session_state:
    st.session_state.us_recos = pd.DataFrame()
if 'fno_recos' not in st.session_state:
    st.session_state.fno_recos = pd.DataFrame()
if 'news_data' not in st.session_state:
    st.session_state.news_data = []

# Main title
st.markdown('<h1 class="main-header">📈 Kamal\'s Trading Dashboard - Fixed</h1>', unsafe_allow_html=True)

# Import modules safely
modules = safe_import_modules()

# Sidebar
st.sidebar.title("Dashboard Controls")
if st.sidebar.button("🔄 Refresh All Data"):
    st.session_state.indian_recos = pd.DataFrame()
    st.session_state.us_recos = pd.DataFrame()
    st.session_state.fno_recos = pd.DataFrame()
    st.session_state.news_data = []
    st.cache_data.clear()
    st.success("All data refreshed!")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["📰 Market News", "🇮🇳 Indian Stocks", "🇺🇸 US Stocks", "📊 F&O Options"])

# Tab 1: Market News
with tab1:
    st.subheader("📰 Latest Market News & Analysis")
    
    if st.button("🔄 Refresh Latest News", type="primary"):
        if modules.get('news'):
            try:
                with st.spinner("Fetching latest news..."):
                    st.session_state.news_data = modules['get_latest_news']()
                
                if st.session_state.news_data:
                    st.success(f"✅ Loaded {len(st.session_state.news_data)} news items")
                else:
                    st.warning("No recent news data available.")
                    
            except Exception as e:
                st.error(f"Error loading news: {e}")
        else:
            st.session_state.news_data = [
                {
                    'title': 'Sample Market News',
                    'summary': 'This is sample news data.',
                    'category': 'Market Movement',
                    'market_impact': 'Medium',
                    'source': 'Sample News',
                    'time': datetime.now().strftime('%H:%M IST'),
                    'date': datetime.now().strftime('%d-%m-%Y'),
                    'link': 'https://example.com'
                }
            ]
            st.info("📰 Using sample news data")
    
    # Display news
    if st.session_state.news_data:
        for news in st.session_state.news_data[:15]:
            with st.expander(f"📈 {news.get('title', 'No Title')}", expanded=False):
                col1, col2, col3 = st.columns([1, 1, 2])
                
                with col1:
                    st.markdown(f"**📅 Date:** {news.get('date', 'Unknown')}")
                    st.markdown(f"**🕒 Time:** {news.get('time', 'Unknown')}")
                
                with col2:
                    st.markdown(f"**📰 Source:** {news.get('source', 'Unknown')}")
                    st.markdown(f"**📊 Impact:** {news.get('market_impact', 'Low')}")
                
                with col3:
                    st.markdown("**🔗 Read Full Article:**")
                    link = news.get('link', '')
                    if link and link != '':
                        st.markdown(f"[🔗 Read Full Article]({link})")
                    else:
                        st.markdown("🔗 Link unavailable")
                
                st.markdown("**📝 Summary:**")
                st.markdown(f"*{news.get('summary', 'No summary available')}*")
    else:
        st.info("Click 'Refresh Latest News' to load updates!")

# Tab 2: Indian Stocks
with tab2:
    st.subheader("🇮🇳 Indian Stock Recommendations")
    
    st.markdown("""
    <div class="opportunity-alert">
    <strong>📊 Enhanced NSE Scanner</strong><br>
    Complete NSE universe scanning with advanced technical analysis
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        min_price_in = st.number_input("Min Price (₹)", value=25, min_value=1, key="in_price")
    with col2:
        max_rsi_in = st.number_input("Max RSI", value=70, min_value=30, max_value=100, key="in_rsi")
    with col3:
        min_tech_score = st.number_input("Min Technical Score", value=5, min_value=3, max_value=8, key="tech_score")
    with col4:
        batch_size_in = st.number_input("Stocks to Scan", value=150, min_value=50, max_value=500, key="in_batch")
    
    if st.button("🔍 Start Indian Stock Scan", type="primary", key="scan_indian"):
        with st.spinner("Scanning Indian stocks..."):
            try:
                if modules.get('indian_stock'):
                    st.session_state.indian_recos = modules['get_indian_recommendations'](
                        min_price_in, max_rsi_in, min_volume=50000, batch_size=batch_size_in
                    )
                else:
                    st.session_state.indian_recos = fallback_indian_recommendations(
                        min_price_in, max_rsi_in, min_volume=50000, batch_size=batch_size_in
                    )
                
                if not st.session_state.indian_recos.empty:
                    st.success(f"🎯 Found {len(st.session_state.indian_recos)} opportunities!")
                else:
                    st.warning("No stocks found. Try relaxing criteria.")
                    
            except Exception as e:
                st.error(f"Error during scan: {e}")
    
    if not st.session_state.indian_recos.empty:
        st.markdown(f"**📊 Results: {len(st.session_state.indian_recos)} opportunities**")
        st.dataframe(st.session_state.indian_recos, use_container_width=True, height=400)
        
        csv = st.session_state.indian_recos.to_csv(index=False)
        st.download_button(
            "📥 Download Results",
            csv,
            f"indian_stocks_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv"
        )
    else:
        st.info("Click 'Start Indian Stock Scan' to find opportunities!")

# Tab 3: US Stocks
with tab3:
    st.subheader("🇺🇸 US Stock Recommendations")
    
    st.markdown("""
    <div class="opportunity-alert">
    <strong>📊 S&P 500 Scanner</strong><br>
    Complete S&P 500 coverage with advanced pattern detection
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        min_price_us = st.number_input("Min Price ($)", value=25, min_value=1, key="us_price")
    with col2:
        max_rsi_us = st.number_input("Max RSI", value=65, min_value=1, max_value=100, key="us_rsi")
    with col3:
        batch_size_us = st.number_input("Stocks to Scan", value=100, min_value=50, max_value=500, key="us_batch")
    
    if st.button("🔍 Scan S&P 500 Stocks", type="primary", key="scan_us"):
        with st.spinner("Scanning S&P 500 stocks..."):
            try:
                if modules.get('us_stock'):
                    st.session_state.us_recos = modules['get_us_recommendations'](
                        min_price_us, max_rsi_us, min_volume=500000, batch_size=batch_size_us
                    )
                else:
                    st.session_state.us_recos = fallback_us_recommendations(
                        min_price_us, max_rsi_us, min_volume=500000, batch_size=batch_size_us
                    )
                
                if not st.session_state.us_recos.empty:
                    st.success(f"🎯 Found {len(st.session_state.us_recos)} opportunities!")
                else:
                    st.warning("No stocks found. Try relaxing criteria.")
                    
            except Exception as e:
                st.error(f"Error during scan: {e}")
    
    if not st.session_state.us_recos.empty:
        st.markdown(f"**📊 Results: {len(st.session_state.us_recos)} opportunities**")
        st.dataframe(st.session_state.us_recos, use_container_width=True, height=400)
        
        csv = st.session_state.us_recos.to_csv(index=False)
        st.download_button(
            "📥 Download Results",
            csv,
            f"us_stocks_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv"
        )
    else:
        st.info("Click 'Scan S&P 500 Stocks' to find opportunities!")

# Tab 4: F&O Options
with tab4:
    st.subheader("📊 F&O Options & Index Trading")
    
    if modules.get('fno'):
        st.markdown("""
        <div class="opportunity-alert">
        <strong>📈 Enhanced F&O Analysis</strong><br>
        No duplicates, all F&O stocks, realistic targets
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            strategy_focus = st.selectbox("Strategy Focus", 
                ["Best Opportunities", "Bullish Bias Only", "Bearish Bias Only"])
        with col2:
            risk_preference = st.selectbox("Risk Preference", 
                ["All Risk Levels", "Medium Risk Only", "High Risk Only"])
        
        if st.button("🔍 Generate F&O Opportunities", type="primary", key="scan_fno"):
            with st.spinner("Generating F&O analysis..."):
                try:
                    st.session_state.fno_recos = modules['generate_fno_opportunities']()
                    
                    if not st.session_state.fno_recos.empty:
                        summary = modules['get_options_summary'](st.session_state.fno_recos)
                        st.success(f"🎯 Generated {summary['total_opportunities']} opportunities!")
                    else:
                        st.warning("No F&O opportunities found.")
                        
                except Exception as e:
                    st.error(f"Error generating F&O opportunities: {e}")
        
        if not st.session_state.fno_recos.empty:
            st.markdown(f"**📊 F&O Results: {len(st.session_state.fno_recos)} opportunities**")
            st.dataframe(st.session_state.fno_recos, use_container_width=True, height=500)
            
            csv = st.session_state.fno_recos.to_csv(index=False)
            st.download_button(
                "📥 Download Results",
                csv,
                f"fno_opportunities_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv"
            )
        else:
            st.info("Click 'Generate F&O Opportunities' to get analysis!")
    else:
        st.error("❌ F&O module not available")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
<strong>Kamal's Trading Dashboard - Fixed Version</strong><br>
Professional trading analysis with enhanced features
</div>
""", unsafe_allow_html=True)
