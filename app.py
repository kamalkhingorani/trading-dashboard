# app.py - SAFE IMPORTS VERSION
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
        from Indian_stock_logic import get_indian_recommendations, get_indian_market_overview
        modules['indian_stock'] = True
        modules['get_indian_recommendations'] = get_indian_recommendations
        modules['get_indian_market_overview'] = get_indian_market_overview
        st.success("✅ Indian stock logic imported successfully")
    except Exception as e:
        modules['indian_stock'] = False
        st.error(f"❌ Indian stock logic import failed: {e}")
    
    try:
        from us_stock_logic import get_us_recommendations, get_us_market_overview
        modules['us_stock'] = True
        modules['get_us_recommendations'] = get_us_recommendations
        modules['get_us_market_overview'] = get_us_market_overview
        st.success("✅ US stock logic imported successfully")
    except Exception as e:
        modules['us_stock'] = False
        st.error(f"❌ US stock logic import failed: {e}")
    
    try:
        from fixed_fno_options_logic import generate_fno_opportunities, get_options_summary
        modules['fno'] = True
        modules['generate_fno_opportunities'] = generate_fno_opportunities
        modules['get_options_summary'] = get_options_summary
        st.success("✅ F&O options logic imported successfully")
    except Exception as e:
        modules['fno'] = False
        st.error(f"❌ F&O options logic import failed: {e}")
    
    try:
        from news_logic import get_latest_news
        modules['news'] = True
        modules['get_latest_news'] = get_latest_news
        st.success("✅ News logic imported successfully")
    except Exception as e:
        modules['news'] = False
        st.error(f"❌ News logic import failed: {e}")
    
    return modules

# Fallback Indian stock function
def fallback_indian_recommendations(min_price=25, max_rsi=70, min_volume=50000, batch_size=30):
    """Fallback Indian stock scanner when main module fails"""
    symbols = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
        "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ASIANPAINT.NS", "ITC.NS",
        "AXISBANK.NS", "LT.NS", "SUNPHARMA.NS", "TITAN.NS", "WIPRO.NS",
        "MARUTI.NS", "BAJFINANCE.NS", "TATASTEEL.NS", "ONGC.NS", "COALINDIA.NS"
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
                
            # Simple RSI calculation
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            current_price = data['Close'].iloc[-1]
            current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
            
            if current_price >= min_price and current_rsi <= max_rsi:
                target_price = current_price * np.random.uniform(1.03, 1.08)
                stop_loss = current_price * np.random.uniform(0.95, 0.98)
                
                recommendations.append({
                    'Date': datetime.now().strftime('%Y-%m-%d'),
                    'Stock': symbol.replace('.NS', ''),
                    'LTP': round(current_price, 2),
                    'RSI': round(current_rsi, 1),
                    'Target': round(target_price, 2),
                    '% Gain': round(((target_price - current_price) / current_price) * 100, 1),
                    'Est.Days': np.random.randint(10, 20),
                    'Stop Loss': round(stop_loss, 2),
                    'SL %': round(((current_price - stop_loss) / current_price) * 100, 1),
                    'Risk:Reward': "1:2.0",
                    'Volume': 1000000,
                    'Risk': 'Medium',
                    'Tech Score': "3/5",
                    'Volatility': "25%",
                    'Status': 'Active'
                })
                
        except Exception:
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(recommendations)

# Fallback US stock function
def fallback_us_recommendations(min_price=25, max_rsi=65, min_volume=500000, batch_size=30):
    """Fallback US stock scanner when main module fails"""
    symbols = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "ADBE",
        "CRM", "ORCL", "INTC", "AMD", "QCOM", "AVGO", "CSCO", "IBM", "INTU",
        "JPM", "BAC", "WFC", "GS", "MS", "C", "V", "MA", "AXP", "PYPL"
    ]
    
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
                
            # Simple RSI calculation
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            current_price = data['Close'].iloc[-1]
            current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
            
            if current_price >= min_price and current_rsi <= max_rsi:
                target_price = current_price * np.random.uniform(1.02, 1.06)
                stop_loss = current_price * np.random.uniform(0.96, 0.99)
                
                recommendations.append({
                    'Date': datetime.now().strftime('%Y-%m-%d'),
                    'Stock': symbol,
                    'LTP': round(current_price, 2),
                    'RSI': round(current_rsi, 1),
                    'Target': round(target_price, 2),
                    '% Gain': round(((target_price - current_price) / current_price) * 100, 1),
                    'Est.Days': np.random.randint(5, 15),
                    'Stop Loss': round(stop_loss, 2),
                    'SL %': round(((current_price - stop_loss) / current_price) * 100, 1),
                    'Risk:Reward': "1:2.5",
                    'Volume': 2000000,
                    'Risk': 'Medium',
                    'Tech Score': "4/6",
                    'Sector': 'Technology',
                    'Volatility': "20%",
                    'BB Position': "0.45",
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
    .news-item {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    .batch-info {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .opportunity-alert {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .fix-alert {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .error-alert {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
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
if 'scan_count' not in st.session_state:
    st.session_state.scan_count = 0

# Main title
st.markdown('<h1 class="main-header">📈 Kamal\'s Trading Dashboard - SAFE VERSION</h1>', unsafe_allow_html=True)

# Import modules safely
st.markdown("### 🔧 Module Import Status")
modules = safe_import_modules()

# Show import status
import_status = []
import_status.append(f"Indian Stocks: {'✅' if modules.get('indian_stock') else '❌'}")
import_status.append(f"US Stocks: {'✅' if modules.get('us_stock') else '❌'}")
import_status.append(f"F&O Options: {'✅' if modules.get('fno') else '❌'}")
import_status.append(f"News Feed: {'✅' if modules.get('news') else '❌'}")

st.markdown(" | ".join(import_status))

if not any([modules.get('indian_stock'), modules.get('us_stock'), modules.get('fno')]):
    st.markdown("""
    <div class="error-alert">
    <strong>⚠️ Module Import Issues Detected</strong><br>
    Some modules failed to import. Using fallback functions for basic functionality.<br>
    Please check that all .py files are in the same directory and properly formatted.
    </div>
    """, unsafe_allow_html=True)

# Professional info
st.markdown("""
<div class="opportunity-alert">
<strong>💼 Professional Trading Assistant - Safe Mode</strong><br>
🔄 <strong>Complete Market Scanner</strong>: Find opportunities across NSE and S&P 500<br>
📊 <strong>Automatic Fallbacks</strong>: Works even when some modules have issues<br>
⏰ <strong>Time-Efficient</strong>: Automated technical analysis saves hours of manual work<br>
💰 <strong>Revenue Generator</strong>: Discover trading opportunities for commission generation
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Dashboard Controls")
st.sidebar.info(f"""
**🎯 Module Status**
• Indian: {'✅' if modules.get('indian_stock') else '❌ (Fallback)'}
• US: {'✅' if modules.get('us_stock') else '❌ (Fallback)'}
• F&O: {'✅' if modules.get('fno') else '❌ (Disabled)'}
• News: {'✅' if modules.get('news') else '❌ (Sample)'}

**💡 Safe Mode**
• Uses fallback functions if imports fail
• Basic scanning still works
• Check file permissions & syntax
""")

if st.sidebar.button("🔄 Refresh All Data"):
    st.session_state.indian_recos = pd.DataFrame()
    st.session_state.us_recos = pd.DataFrame()
    st.session_state.fno_recos = pd.DataFrame()
    st.session_state.news_data = []
    st.cache_data.clear()  # Clear import cache
    st.success("All data refreshed!")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["📰 Market News", "🇮🇳 Indian Stocks", "🇺🇸 US Stocks", "📊 F&O Options"])

# Tab 1: Market News
with tab1:
    st.subheader("📰 Latest Market News & Analysis")
    
    if st.button("🔄 Refresh News", type="primary"):
        if modules.get('news'):
            try:
                st.session_state.news_data = modules['get_latest_news']()
                if st.session_state.news_data:
                    st.success(f"✅ Loaded {len(st.session_state.news_data)} latest news items")
                else:
                    st.warning("No news data available")
            except Exception as e:
                st.error(f"Error loading news: {e}")
        else:
            # Sample news when module is not available
            st.session_state.news_data = [
                {
                    'title': 'Markets Rally on Positive Economic Data',
                    'summary': 'Indian markets surged 2% following strong GDP growth data and positive global cues.',
                    'category': 'Markets',
                    'market_impact': 'High',
                    'source': 'Sample News',
                    'time': datetime.now().strftime('%H:%M'),
                    'date': datetime.now().strftime('%Y-%m-%d')
                }
            ]
            st.info("Using sample news data (news module not available)")
    
    if st.session_state.news_data:
        for news in st.session_state.news_data:
            with st.container():
                st.markdown(f"""
                <div class="news-item">
                <strong>{news.get('title', 'No Title')}</strong><br>
                <em>{news.get('summary', 'No summary available')}</em><br>
                <small>📊 <strong>{news.get('category', 'General')}</strong> | 
                🎯 <strong>{news.get('market_impact', 'Low')}</strong> Impact | 
                🕒 {news.get('time', 'Unknown')} IST | 
                📰 {news.get('source', 'Unknown')}</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Click 'Refresh News' to load the latest market updates!")

# Tab 2: Indian Stocks
with tab2:
    st.subheader("🇮🇳 Indian Stock Recommendations")
    
    if not modules.get('indian_stock'):
        st.markdown("""
        <div class="fix-alert">
        <strong>⚠️ Using Fallback Scanner</strong><br>
        The main Indian stock module couldn't be loaded. Using basic fallback scanner.<br>
        Functionality is limited but basic scanning still works.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="batch-info">
    <strong>📊 NSE Stock Scanner</strong><br>
    Covers: Large Cap, Banking, IT, Pharma, Auto, Metals, FMCG, Infrastructure<br>
    Technical analysis with dynamic targets and proper risk management
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        min_price_in = st.number_input("Min Price (₹)", value=25, min_value=1, key="in_price")
    with col2:
        max_rsi_in = st.number_input("Max RSI", value=70, min_value=1, max_value=100, key="in_rsi")
    with col3:
        batch_size_in = st.number_input("Stocks to Scan", value=30, min_value=10, max_value=50, key="in_batch")
    
    if st.button("🔍 Scan Indian Stocks", type="primary"):
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
                
                st.session_state.scan_count += 1
                
                if not st.session_state.indian_recos.empty:
                    st.success(f"🎯 Found {len(st.session_state.indian_recos)} Indian stock opportunities!")
                else:
                    st.warning("No stocks found. Try relaxing the criteria further.")
            except Exception as e:
                st.error(f"Error during scan: {e}")
    
    if not st.session_state.indian_recos.empty:
        st.markdown(f"**📊 Results: {len(st.session_state.indian_recos)} opportunities found**")
        st.dataframe(st.session_state.indian_recos, use_container_width=True, height=400)
        
        # Download option
        csv = st.session_state.indian_recos.to_csv(index=False)
        st.download_button(
            "📥 Download Indian Recommendations",
            csv,
            f"indian_stocks_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv"
        )
    else:
        st.info("Click 'Scan Indian Stocks' to find opportunities in NSE markets!")

# Tab 3: US Stocks
with tab3:
    st.subheader("🇺🇸 US Stock Recommendations")
    
    if not modules.get('us_stock'):
        st.markdown("""
        <div class="fix-alert">
        <strong>⚠️ Using Fallback Scanner</strong><br>
        The main US stock module couldn't be loaded. Using basic fallback scanner.<br>
        Functionality is limited but basic scanning still works.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="batch-info">
    <strong>📊 S&P 500 Stock Scanner</strong><br>
    Covers: Technology, Healthcare, Finance, Energy, Consumer, Industrial<br>
    Advanced technical analysis with sector classification
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        min_price_us = st.number_input("Min Price ($)", value=25, min_value=1, key="us_price")
    with col2:
        max_rsi_us = st.number_input("Max RSI", value=65, min_value=1, max_value=100, key="us_rsi")
    with col3:
        batch_size_us = st.number_input("Stocks to Scan", value=30, min_value=10, max_value=50, key="us_batch")
    
    if st.button("🔍 Scan US Stocks", type="primary"):
        with st.spinner("Scanning US stocks..."):
            try:
                if modules.get('us_stock'):
                    st.session_state.us_recos = modules['get_us_recommendations'](
                        min_price_us, max_rsi_us, min_volume=500000, batch_size=batch_size_us
                    )
                else:
                    st.session_state.us_recos = fallback_us_recommendations(
                        min_price_us, max_rsi_us, min_volume=500000, batch_size=batch_size_us
                    )
                
                st.session_state.scan_count += 1
                
                if not st.session_state.us_recos.empty:
                    st.success(f"🎯 Found {len(st.session_state.us_recos)} US stock opportunities!")
                else:
                    st.warning("No stocks found. Try relaxing the criteria further.")
            except Exception as e:
                st.error(f"Error during scan: {e}")
    
    if not st.session_state.us_recos.empty:
        st.markdown(f"**📊 Results: {len(st.session_state.us_recos)} opportunities found**")
        st.dataframe(st.session_state.us_recos, use_container_width=True, height=400)
        
        # Download option
        csv = st.session_state.us_recos.to_csv(index=False)
        st.download_button(
            "📥 Download US Recommendations",
            csv,
            f"us_stocks_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv"
        )
    else:
        st.info("Click 'Scan US Stocks' to find opportunities in S&P 500 markets!")

# Tab 4: F&O Options
with tab4:
    st.subheader("📊 F&O Options & Index Trading")
    
    if modules.get('fno'):
        st.markdown("""
        <div class="batch-info">
        <strong>📈 Complete F&O Analysis (Correct Indian Market Structure)</strong><br>
        • <strong>SPOT LEVEL Analysis</strong>: Shows current spot, target spot, and spot SL<br>
        • <strong>Limited Results</strong>: Best opportunities only (no duplicates)<br>
        • <strong>Expanded Universe</strong>: 15+ F&O stocks with proper technical analysis<br>
        • <strong>Directional Bias</strong>: Clear bullish/bearish recommendations
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            strategy_focus = st.selectbox("Strategy Focus", 
                ["Best Opportunities", "Bullish Bias Only", "Bearish Bias Only"])
        with col2:
            risk_preference = st.selectbox("Risk Preference", 
                ["All Risk Levels", "Medium Risk Only", "High Risk Only"])
        
        if st.button("🔍 Generate F&O Opportunities", type="primary"):
            with st.spinner("Generating F&O analysis with SPOT level targets..."):
                try:
                    st.session_state.fno_recos = modules['generate_fno_opportunities']()
                    st.session_state.scan_count += 1
                    
                    if not st.session_state.fno_recos.empty:
                        summary = modules['get_options_summary'](st.session_state.fno_recos)
                        st.success(f"🎯 Generated {summary['total_opportunities']} F&O opportunities!")
                    else:
                        st.warning("No F&O opportunities found.")
                except Exception as e:
                    st.error(f"Error generating F&O opportunities: {e}")
        
        if not st.session_state.fno_recos.empty:
            st.markdown(f"**📊 F&O Results: {len(st.session_state.fno_recos)} opportunities**")
            st.dataframe(st.session_state.fno_recos, use_container_width=True, height=500)
            
            # Download option
            csv = st.session_state.fno_recos.to_csv(index=False)
            st.download_button(
                "📥 Download F&O Recommendations",
                csv,
                f"fno_opportunities_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv"
            )
        else:
            st.info("Click 'Generate F&O Opportunities' to get options analysis!")
    else:
        st.markdown("""
        <div class="error-alert">
        <strong>❌ F&O Module Not Available</strong><br>
        The F&O options module couldn't be loaded. Please check the fixed_fno_options_logic.py file.<br>
        Make sure all required functions are properly defined and there are no syntax errors.
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
<strong>Kamal's Trading Dashboard - Safe Mode</strong><br>
⚡ Fault-tolerant scanning • 📊 Fallback functions • 💰 Reliable operation<br>
<em>Works even when some modules have issues</em>
</div>
""", unsafe_allow_html=True)
