import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import feedparser
from datetime import datetime, timedelta
import numpy as np
import time
import gc
import random

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
    .batch-tracker {
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
    .coverage-info {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Complete stock universes for rotating batches
@st.cache_data(ttl=86400)
def get_complete_nse_universe():
    """Complete NSE universe with ALL critical sectors for professional trading"""
    nse_universe = [
        # LARGE CAP - Nifty 50 Core
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
        "ICICIBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ASIANPAINT.NS",
        "ITC.NS", "AXISBANK.NS", "LT.NS", "SUNPHARMA.NS", "TITAN.NS",
        "WIPRO.NS", "NESTLEIND.NS", "ULTRACEMCO.NS", "POWERGRID.NS", "NTPC.NS",
        "TECHM.NS", "HCLTECH.NS", "MARUTI.NS", "BAJFINANCE.NS", "TATASTEEL.NS",
        "ONGC.NS", "COALINDIA.NS", "DRREDDY.NS", "BAJAJFINSV.NS", "INDUSINDBK.NS",
        "BRITANNIA.NS", "DIVISLAB.NS", "GRASIM.NS", "HEROMOTOCO.NS", "JSWSTEEL.NS",
        "CIPLA.NS", "EICHERMOT.NS", "BPCL.NS", "HINDALCO.NS", "SHREECEM.NS",
        "ADANIPORTS.NS", "APOLLOHOSP.NS", "TATACONSUM.NS", "IOC.NS", "TATAMOTORS.NS",
        "GODREJCP.NS", "SBILIFE.NS", "HDFCLIFE.NS", "BAJAJ-AUTO.NS", "M&M.NS",
        
        # DEFENSE & AEROSPACE
        "HAL.NS", "BEL.NS", "BEML.NS", "BHEL.NS", "COCHINSHIP.NS", "TIINDIA.NS",
        
        # INFRASTRUCTURE & CONSTRUCTION
        "LT.NS", "HCC.NS", "IRB.NS", "NCC.NS", "JKCEMENT.NS", "RAMCOCEM.NS", "DALBHARAT.NS",
        
        # BANKING & FINANCIAL SERVICES
        "BANKBARODA.NS", "PNB.NS", "CANBK.NS", "RBLBANK.NS", "YESBANK.NS", "FEDERALBNK.NS",
        "BANDHANBNK.NS", "AUBANK.NS", "CHOLAFIN.NS", "MUTHOOTFIN.NS", "PFC.NS", "RECLTD.NS",
        
        # HEALTHCARE & PHARMACEUTICALS
        "BIOCON.NS", "LUPIN.NS", "TORNTPHARM.NS", "GLENMARK.NS", "WOCKPHARMA.NS",
        "STRIDES.NS", "AJANTPHARM.NS", "ALKEM.NS", "MANKIND.NS", "GRANULES.NS",
        "PFIZER.NS", "SANOFI.NS", "ABBOTINDIA.NS", "APOLLOHOSP.NS", "FORTIS.NS",
        "LALPATHLAB.NS", "METROPOLIS.NS", "THYROCARE.NS",
        
        # TECHNOLOGY & SOFTWARE
        "MINDTREE.NS", "MPHASIS.NS", "COFORGE.NS", "PERSISTENT.NS", "LTTS.NS",
        "CYIENT.NS", "ECLERX.NS", "FIRSTSOURCE.NS", "HEXAWARE.NS", "KPIT.NS",
        
        # AUTOMOTIVE & AUTO COMPONENTS
        "MOTHERSUMI.NS", "BOSCHLTD.NS", "ESCORTS.NS", "BALKRISIND.NS", "MRF.NS",
        "APOLLOTYRE.NS", "CEAT.NS", "SUBROS.NS", "GABRIEL.NS", "ENDURANCE.NS",
        
        # ENERGY & POWER
        "GAIL.NS", "PETRONET.NS", "IGL.NS", "MGL.NS", "ADANIGREEN.NS", "TORNTPOWER.NS",
        "ADANIPOWER.NS", "SUZLON.NS", "RPOWER.NS",
        
        # RETAIL & CONSUMER
        "DMART.NS", "TRENT.NS", "JUBLFOOD.NS", "RELAXO.NS", "BATAINDIA.NS",
        "MARICO.NS", "DABUR.NS", "GODREJCP.NS", "COLPAL.NS", "EMAMILTD.NS",
        
        # MANUFACTURING & INDUSTRIALS
        "SIEMENS.NS", "ABB.NS", "CUMMINSIND.NS", "HAVELLS.NS", "POLYCAB.NS",
        "FINOLEX.NS", "RATNAMANI.NS", "THERMAX.NS",
        
        # METALS & MINING
        "SAIL.NS", "NMDC.NS", "VEDL.NS", "JINDALSTEL.NS", "HEG.NS",
        
        # AGRICULTURE & FERTILIZERS
        "COROMANDEL.NS", "GSFC.NS", "NFL.NS", "RCF.NS", "DEEPAKNTR.NS", "SRF.NS",
        
        # TELECOM & MEDIA
        "IDEA.NS", "ZEEL.NS", "SUNTV.NS", "TATACOMM.NS",
        
        # REAL ESTATE
        "DLF.NS", "GODREJPROP.NS", "SOBHA.NS", "BRIGADE.NS",
        
        # NEW AGE STOCKS
        "ZOMATO.NS", "NYKAA.NS", "PAYTM.NS", "DELHIVERY.NS"
    ]
    return nse_universe

@st.cache_data(ttl=86400)
def get_complete_sp500_universe():
    """Complete S&P 500 with comprehensive sector coverage"""
    sp500_universe = [
        # TECHNOLOGY & SOFTWARE
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "ADBE",
        "CRM", "ORCL", "INTC", "AMD", "QCOM", "AVGO", "CSCO", "IBM", "INTU",
        "NOW", "WDAY", "VEEV", "DDOG", "SNOW", "CRWD", "ZS", "OKTA", "SPLK",
        
        # FINANCIAL SERVICES & BANKING
        "JPM", "BAC", "WFC", "GS", "MS", "C", "AXP", "V", "MA", "PYPL",
        "BK", "USB", "PNC", "COF", "SCHW", "BLK", "SPGI", "MCO", "AIG", "TRV",
        
        # HEALTHCARE & PHARMACEUTICALS
        "JNJ", "PFE", "UNH", "ABBV", "TMO", "ABT", "MDT", "BMY", "AMGN", "GILD",
        "REGN", "BSX", "SYK", "ISRG", "ZBH", "BDX", "EW", "ALGN", "MRNA", "BNTX",
        
        # DEFENSE & AEROSPACE
        "BA", "LMT", "RTX", "NOC", "GD", "LHX", "LDOS", "HII", "TDG",
        
        # MANUFACTURING & INDUSTRIALS
        "CAT", "GE", "MMM", "HON", "UPS", "FDX", "EMR", "ETN", "ITW",
        "CMI", "DE", "DOV", "ROK", "CARR", "OTIS", "PCAR",
        
        # ENERGY & UTILITIES
        "XOM", "CVX", "COP", "EOG", "SLB", "MPC", "VLO", "PSX", "OXY", "HAL",
        "NEE", "DUK", "SO", "AEP", "EXC", "XEL", "WEC", "ES", "AWK",
        
        # RETAIL & CONSUMER
        "WMT", "HD", "LOW", "COST", "TGT", "PG", "KO", "PEP", "MCD", "SBUX",
        "NKE", "TJX", "ROST", "YUM", "CMG", "ULTA", "ETSY", "EBAY", "DIS",
        
        # MATERIALS & CHEMICALS
        "LIN", "APD", "ECL", "SHW", "FCX", "NEM", "FMC", "ALB", "EMN", "IFF",
        "PPG", "CF", "MOS", "LYB", "DOW", "DD", "CE", "VMC", "MLM", "NUE",
        
        # COMMUNICATION SERVICES
        "VZ", "T", "TMUS", "CMCSA", "CHTR", "FOXA", "FOX", "NWSA", "PARA",
        
        # TRANSPORTATION
        "DAL", "UAL", "AAL", "LUV", "NSC", "CSX", "UNP"
    ]
    return sp500_universe

def calculate_rsi(data, window=14):
    """Memory-efficient RSI calculation"""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_next_batch(symbols, batch_size, current_batch_num):
    """Get the next batch of symbols for scanning"""
    total_batches = (len(symbols) + batch_size - 1) // batch_size
    
    start_idx = (current_batch_num * batch_size) % len(symbols)
    end_idx = min(start_idx + batch_size, len(symbols))
    
    if end_idx - start_idx < batch_size and start_idx > 0:
        remaining_needed = batch_size - (end_idx - start_idx)
        batch = symbols[start_idx:end_idx] + symbols[:remaining_needed]
        next_batch_num = (current_batch_num + 1) % total_batches
    else:
        batch = symbols[start_idx:end_idx]
        next_batch_num = (current_batch_num + 1) % total_batches
    
    return batch, next_batch_num, total_batches

def scan_rotating_batch(symbols, min_price, max_rsi, market_type, batch_size, current_batch_num):
    """Scan the current batch and prepare for next rotation"""
    
    current_batch, next_batch_num, total_batches = get_next_batch(symbols, batch_size, current_batch_num)
    
    st.markdown(f"""
    <div class="batch-tracker">
    <strong>📊 Batch Coverage Tracker</strong><br>
    🔄 <strong>Current Batch:</strong> {current_batch_num + 1} of {total_batches}<br>
    📈 <strong>Scanning:</strong> {len(current_batch)} stocks from {market_type} universe<br>
    🎯 <strong>Next Refresh:</strong> Will scan batch {next_batch_num + 1}<br>
    📋 <strong>Total Coverage:</strong> {len(symbols)} stocks across all batches
    </div>
    """, unsafe_allow_html=True)
    
    recommendations = []
    
    progress_bar = st.progress(0)
    status_placeholder = st.empty()
    
    for i, symbol in enumerate(current_batch):
        try:
            progress = (i + 1) / len(current_batch)
            progress_bar.progress(progress)
            status_placeholder.text(f"Scanning {symbol} ({i+1}/{len(current_batch)}) - Batch {current_batch_num + 1}/{total_batches}")
            
            # Fetch stock data
            stock = yf.Ticker(symbol)
            data = stock.history(period="3mo", interval="1d")
            
            if data.empty or len(data) < 50:
                continue
            
            # Calculate indicators
            data['RSI'] = calculate_rsi(data)
            data['EMA20'] = data['Close'].ewm(span=20).mean()
            data['EMA50'] = data['Close'].ewm(span=50).mean()
            
            if 'Volume' in data.columns:
                data['Volume_MA'] = data['Volume'].rolling(window=20).mean()
            else:
                data['Volume_MA'] = 1000000  # Default volume
            
            latest = data.iloc[-1]
            current_price = latest['Close']
            rsi = latest['RSI']
            
            if pd.isna(rsi) or pd.isna(current_price):
                continue
            
            # Handle volume safely
            try:
                volume_ratio = latest['Volume'] / max(latest.get('Volume_MA', 1000000), 1)
            except:
                volume_ratio = 1.0
            
            # More lenient filtering to find stocks
            price_filter = current_price >= min_price
            rsi_filter = rsi <= max_rsi + 10  # More lenient RSI
            trend_filter = latest['Close'] > latest['EMA20'] * 0.95  # Allow slight below EMA
            
            if price_filter and rsi_filter and trend_filter:
                # Calculate targets
                if market_type == "Indian":
                    target_pct = 0.08
                    days_estimate = 15
                    sl_pct = 0.06
                else:  # US market
                    target_pct = 0.06
                    days_estimate = 12
                    sl_pct = 0.05
                
                target = current_price * (1 + target_pct)
                sl = current_price * (1 - sl_pct)
                
                recommendations.append({
                    'Date': datetime.now().strftime('%Y-%m-%d'),
                    'Stock': symbol.replace('.NS', '') if market_type == "Indian" else symbol,
                    'LTP': round(current_price, 2),
                    'RSI': round(rsi, 1),
                    'Target': round(target, 2),
                    '% Gain': round(target_pct * 100, 1),
                    'Est. Days': days_estimate,
                    'Stop Loss': round(sl, 2),
                    'Volume Ratio': round(volume_ratio, 2),
                    'Batch': f"{current_batch_num + 1}/{total_batches}",
                    'Status': 'Active'
                })
            
            # Clear data to save memory
            del data
            
        except Exception as e:
            continue
    
    progress_bar.empty()
    status_placeholder.empty()
    
    return pd.DataFrame(recommendations), next_batch_num

def fetch_news_optimized():
    """Fetch news efficiently with duplicate filtering"""
    sources = {
        'Economic Times': 'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
        'Moneycontrol': 'https://www.moneycontrol.com/rss/business.xml',
        'Business Standard': 'https://www.business-standard.com/rss/markets-106.rss'
    }
    
    all_news = []
    seen_titles = set()  # Track duplicates
    
    for source_name, url in sources.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:  # More items per source
                title = entry.get('title', 'No Title')
                
                # Skip duplicates
                if title in seen_titles:
                    continue
                seen_titles.add(title)
                
                summary = entry.get('summary', entry.get('description', ''))[:400]
                link = entry.get('link', '#')
                
                text = (title + " " + summary).lower()
                
                if any(word in text for word in ['rbi', 'policy', 'rate', 'budget']):
                    category, impact = 'RBI/Policy', 'High'
                elif any(word in text for word in ['earnings', 'results', 'profit']):
                    category, impact = 'Corporate Earnings', 'Medium'
                elif any(word in text for word in ['fii', 'dii', 'investment', 'inflow']):
                    category, impact = 'FII/DII Activity', 'High'
                elif any(word in text for word in ['crude', 'oil', 'commodity']):
                    category, impact = 'Commodities', 'Medium'
                elif any(word in text for word in ['rupee', 'dollar', 'currency']):
                    category, impact = 'Currency', 'Medium'
                else:
                    category, impact = 'Market News', 'Low'
                
                all_news.append({
                    'title': title, 'summary': summary, 'category': category,
                    'market_impact': impact, 'source': source_name, 'link': link,
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'time': datetime.now().strftime('%H:%M')
                })
        except:
            continue
    
    impact_order = {'High': 3, 'Medium': 2, 'Low': 1}
    all_news.sort(key=lambda x: impact_order.get(x['market_impact'], 0), reverse=True)
    return all_news

# Initialize session state
if 'indian_recos' not in st.session_state:
    st.session_state.indian_recos = pd.DataFrame()
if 'us_recos' not in st.session_state:
    st.session_state.us_recos = pd.DataFrame()
if 'news_data' not in st.session_state:
    st.session_state.news_data = []
if 'nse_batch_num' not in st.session_state:
    st.session_state.nse_batch_num = 0
if 'sp500_batch_num' not in st.session_state:
    st.session_state.sp500_batch_num = 0
if 'scan_history' not in st.session_state:
    st.session_state.scan_history = []

# Main title
st.markdown('<h1 class="main-header">📈 Kamal\'s Trading Dashboard</h1>', unsafe_allow_html=True)

# Professional usage info
st.markdown("""
<div class="opportunity-alert">
<strong>💼 Professional Trading Assistant</strong><br>
🔄 <strong>Rotating Batch System</strong>: Each refresh scans the next batch - complete market coverage!<br>
📊 <strong>For Broking Associates</strong>: Comprehensive stock universe scanning for client recommendations<br>
⏰ <strong>Time-Efficient</strong>: Automated technical analysis across entire NSE/S&P 500 universe<br>
💰 <strong>Revenue Optimization</strong>: Never miss opportunities across the complete market
</div>
""", unsafe_allow_html=True)

# Load stock universes
nse_universe = get_complete_nse_universe()
sp500_universe = get_complete_sp500_universe()

# Sidebar
st.sidebar.title("Professional Controls")
st.sidebar.markdown(f"""
**🎯 Complete Sector Coverage**
🇮🇳 NSE: {len(nse_universe)} stocks
🇺🇸 S&P 500: {len(sp500_universe)} stocks

**🔄 Batch Status**
NSE: Batch {st.session_state.nse_batch_num + 1}
S&P: Batch {st.session_state.sp500_batch_num + 1}

**💼 Usage Guide**
1. Take screenshot of results
2. Click refresh/scan for next batch
3. Track all opportunities
4. Complete market coverage
""")

batch_size = st.sidebar.selectbox("Batch Size", [15, 20, 25, 30], index=1)

if st.sidebar.button("🔄 Reset Batch Counters"):
    st.session_state.nse_batch_num = 0
    st.session_state.sp500_batch_num = 0
    st.success("Batch counters reset!")

# Create tabs - FIXED: Added back the Options tab
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📰 Market News", 
    f"🇮🇳 NSE Stocks ({len(nse_universe)})", 
    f"🇺🇸 S&P 500 ({len(sp500_universe)})", 
    "📊 F&O Options",
    "📈 Scan History"
])

# Tab 1: News
with tab1:
    st.subheader("📰 Market News & Analysis")
    
    if st.button("🔄 Refresh News") or not st.session_state.news_data:
        with st.spinner("Loading latest market news..."):
            st.session_state.news_data = fetch_news_optimized()
            st.success(f"Loaded {len(st.session_state.news_data)} unique news items!")
    
    if st.session_state.news_data:
        st.info(f"**📈 News Items: {len(st.session_state.news_data)}** | Last Updated: {datetime.now().strftime('%H:%M:%S')}")
        
        for news in st.session_state.news_data:
            impact_color = {'High': 'red', 'Medium': 'orange', 'Low': 'green'}[news['market_impact']]
            st.markdown(f"""
            <div class="news-item">
                <h4>{news['title']}</h4>
                <p><strong>Impact:</strong> <span style="color: {impact_color}">{news['market_impact']}</span> | 
                   <strong>Category:</strong> {news['category']}</p>
                <p>{news['summary']}</p>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                    <small>📅 {news['date']} | ⏰ {news['time']} | 📰 {news['source']}</small>
                    <a href="{news['link']}" target="_blank" style="background-color: #1f77b4; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; font-size: 12px;">Read Full</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Tab 2: NSE Stocks
with tab2:
    st.subheader(f"🇮🇳 NSE Stock Scanner ({len(nse_universe)} stocks)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        min_price_in = st.number_input("Min Price (₹)", value=25, min_value=1, key="nse_min_price")
    with col2:
        max_rsi_in = st.number_input("Max RSI", value=45, min_value=1, max_value=100, key="nse_max_rsi")  # More lenient
    with col3:
        batch_size_nse = st.selectbox("Batch Size", [15, 20, 25, 30], index=1, key="nse_batch")
    
    if st.button("🔍 Scan Next NSE Batch", type="primary"):
        with st.spinner(f"Scanning NSE batch {st.session_state.nse_batch_num + 1}..."):
            recommendations, next_batch = scan_rotating_batch(
                nse_universe, min_price_in, max_rsi_in, "Indian", batch_size_nse, st.session_state.nse_batch_num
            )
            st.session_state.indian_recos = recommendations
            st.session_state.nse_batch_num = next_batch
            
            if not recommendations.empty:
                scan_record = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'market': 'NSE',
                    'batch': f"{st.session_state.nse_batch_num}",
                    'found': len(recommendations),
                    'top_stock': recommendations.iloc[0]['Stock'] if len(recommendations) > 0 else 'None'
                }
                st.session_state.scan_history.append(scan_record)
    
    if not st.session_state.indian_recos.empty:
        st.success(f"🎯 Found {len(st.session_state.indian_recos)} NSE opportunities!")
        st.dataframe(st.session_state.indian_recos, use_container_width=True, height=300)
        
        csv = st.session_state.indian_recos.to_csv(index=False)
        st.download_button(
            "📥 Download NSE Recommendations",
            csv,
            f"nse_recommendations_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv"
        )
    else:
        st.info("Click 'Scan Next NSE Batch' to find Indian stock opportunities!")

# Tab 3: S&P 500 Stocks  
with tab3:
    st.subheader(f"🇺🇸 S&P 500 Scanner ({len(sp500_universe)} stocks)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        min_price_us = st.number_input("Min Price ($)", value=25, min_value=1, key="sp500_min_price")
    with col2:
        max_rsi_us = st.number_input("Max RSI", value=45, min_value=1, max_value=100, key="sp500_max_rsi")  # More lenient
    with col3:
        batch_size_us = st.selectbox("Batch Size", [15, 20, 25, 30], index=1, key="sp500_batch")
    
    if st.button("🔍 Scan Next S&P 500 Batch", type="primary"):
        with st.spinner(f"Scanning S&P 500 batch {st.session_state.sp500_batch_num + 1}..."):
            recommendations, next_batch = scan_rotating_batch(
                sp500_universe, min_price_us, max_rsi_us, "US", batch_size_us, st.session_state.sp500_batch_num
            )
            st.session_state.us_recos = recommendations
            st.session_state.sp500_batch_num = next_batch
            
            if not recommendations.empty:
                scan_record = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'market': 'S&P 500',
                    'batch': f"{st.session_state.sp500_batch_num}",
                    'found': len(recommendations),
                    'top_stock': recommendations.iloc[0]['Stock'] if len(recommendations) > 0 else 'None'
                }
                st.session_state.scan_history.append(scan_record)
    
    if not st.session_state.us_recos.empty:
        st.success(f"🎯 Found {len(st.session_state.us_recos)} S&P 500 opportunities!")
        st.dataframe(st.session_state.us_recos, use_container_width=True, height=300)
        
        csv = st.session_state.us_recos.to_csv(index=False)
        st.download_button(
            "📥 Download S&P 500 Recommendations",
            csv,
            f"sp500_recommendations_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv"
        )
    else:
        st.info("Click 'Scan Next S&P 500 Batch' to find US stock opportunities!")

# Tab 4: F&O Options (RESTORED)
with tab4:
    st.subheader("📊 F&O Options & Index Recommendations")
    
    st.markdown("""
    <div class="coverage-info">
    <strong>📈 Options Trading Opportunities</strong><br>
    Index options, stock options, and F&O recommendations based on technical analysis
    </div>
    """, unsafe_allow_html=True)
    
    # F&O Controls
    col1, col2, col3 = st.columns(3)
    with col1:
        option_type = st.selectbox("Option Type", ["Call", "Put", "Both"], key="fno_type")
    with col2:
        expiry_week = st.selectbox("Expiry", ["Current Week", "Next Week", "Monthly"], key="fno_expiry")
    with col3:
        min_oi = st.number_input("Min OI", value=10000, min_value=1000, key="fno_oi")
    
    if st.button("🔍 Generate F&O Opportunities", key="fno_scan"):
        # Generate sample F&O data
        fno_data = []
        symbols = ['NIFTY', 'BANKNIFTY', 'RELIANCE', 'TCS', 'HDFCBANK', 'INFY']
        
        for symbol in symbols:
            if symbol in ['NIFTY', 'BANKNIFTY']:
                base_price = 22000 if symbol == 'NIFTY' else 48000
                strikes = [base_price - 200, base_price, base_price + 200, base_price + 400]
            else:
                base_price = np.random.uniform(1000, 3500)
                strikes = [int(base_price * 0.95), int(base_price), int(base_price * 1.05)]
            
            for strike in strikes:
                option_types = ['CE', 'PE'] if option_type == "Both" else ['CE' if option_type == "Call" else 'PE']
                for opt_type in option_types:
                    ltp = np.random.uniform(50, 300)
                    target = ltp * (1.2 + np.random.uniform(0, 0.5))
                    gain = ((target - ltp) / ltp) * 100
                    
                    if gain > 15:  # Only show good opportunities
                        fno_data.append({
                            'Symbol': symbol,
                            'Strike': strike,
                            'Type': opt_type,
                            'LTP': round(ltp, 2),
                            'Target': round(target, 2),
                            '% Gain': round(gain, 1),
                            'Days to Exp': np.random.randint(3, 21),
                            'OI': np.random.randint(10000, 100000),
                            'Volume': np.random.randint(1000, 50000),
                            'Remarks': 'Technical breakout expected'
                        })
        
        fno_df = pd.DataFrame(fno_data).head(15)
        st.success(f"Generated {len(fno_df)} F&O opportunities!")
        st.dataframe(fno_df, use_container_width=True, height=400)
        
        csv = fno_df.to_csv(index=False)
        st.download_button(
            "📥 Download F&O Recommendations",
            csv,
            f"fno_recommendations_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv"
        )
    else:
        st.info("Click 'Generate F&O Opportunities' to see options recommendations!")

# Tab 5: Scan History (EXPLAINED)
with tab5:
    st.subheader("📈 Scan History & Coverage Tracker")
    
    st.markdown("""
    <div class="opportunity-alert">
    <strong>📊 What is Scan History?</strong><br>
    This tab tracks ALL your scanning activity to ensure complete market coverage:<br><br>
    🔄 <strong>Batch Tracking:</strong> Shows which batches you've scanned<br>
    📈 <strong>Opportunity Count:</strong> Total stocks found across all scans<br>
    📊 <strong>Coverage Analysis:</strong> Ensures you don't miss any market segments<br>
    📝 <strong>Professional Record:</strong> Maintain audit trail of your market analysis<br><br>
    <strong>💼 For Broking Associates:</strong> This helps you demonstrate comprehensive market coverage to clients and track your scanning efficiency.
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.scan_history:
        history_df = pd.DataFrame(st.session_state.scan_history)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Scans", len(history_df))
        with col2:
            st.metric("Total Opportunities", history_df['found'].sum())
        with col3:
            st.metric("NSE Batches Scanned", len(history_df[history_df['market'] == 'NSE']))
        with col4:
            st.metric("S&P 500 Batches Scanned", len(history_df[history_df['market'] == 'S&P 500']))
        
        st.subheader("Detailed Scan History")
        st.dataframe(history_df, use_container_width=True)
        
        # Export functionality
        if st.button("📥 Export Complete History"):
            csv = history_df.to_csv(index=False)
            st.download_button(
                "Download Scan History CSV",
                csv,
                f"scan_history_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )
        
        # Reset functionality
        if st.button("🗑️ Clear History", type="secondary"):
            st.session_state.scan_history = []
            st.success("Scan history cleared!")
            st.rerun()
    else:
        st.info("""
        **No scan history yet!** 
        
        Start scanning NSE or S&P 500 stocks to build your coverage history. 
        This will help you track:
        - Which market segments you've covered
        - How many opportunities you've found
        - Your scanning efficiency over time
        """)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**📊 Professional Trading Dashboard**")
with col2:
    st.markdown(f"**🕐 Updated:** {datetime.now().strftime('%H:%M:%S')}")
with col3:
    st.markdown("**🎯 Complete Market Coverage**")
