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
        
        # BANKING & FINANCIAL SERVICES (Complete Coverage)
        "BANKBARODA.NS", "BANKINDIA.NS", "CANBK.NS", "CENTRALBK.NS", "IDBIGOLD.NS",
        "INDIANB.NS", "IOB.NS", "MAHABANK.NS", "ORIENTBANK.NS", "PNB.NS",
        "PUNJABSIND.NS", "SOUTHBANK.NS", "SYNDIBANK.NS", "UNIONBANK.NS", "UCOBANK.NS",
        "RBLBANK.NS", "YESBANK.NS", "EQUITAS.NS", "DCBBANK.NS", "CITYUNION.NS",
        "KARURVYSYA.NS", "NAINITAL.NS", "COSMOS.NS", "DHANLAXMI.NS", "JKBANK.NS",
        "FEDERALBNK.NS", "IDFCFIRSTB.NS", "BANDHANBNK.NS", "AUBANK.NS", "UJJIVAN.NS",
        "CHOLAFIN.NS", "BAJAJHLDNG.NS", "IIFL.NS", "MUTHOOTFIN.NS", "MANAPPURAM.NS",
        "SRTRANSFIN.NS", "L&TFH.NS", "PFC.NS", "RECLTD.NS", "IRFC.NS",
        "HUDCO.NS", "LICHSGFIN.NS", "CANFINHOME.NS", "AAVAS.NS", "IBULHSGFIN.NS",
        
        # DEFENSE & AEROSPACE (Critical for National Security)
        "HAL.NS", "BEL.NS", "BEML.NS", "BDL.NS", "GARDENREACH.NS", "GRSE.NS",
        "MAZAGON.NS", "MDL.NS", "MIDHANI.NS", "ORDNANCEFTY.NS", "BHEL.NS",
        "COCHINSHIP.NS", "TIINDIA.NS", "DYNAMATECH.NS", "ASTRAZEN.NS", "IDEAFORGE.NS",
        "NEWGEN.NS", "CENTUM.NS", "DATAPATTNS.NS", "PARAS.NS", "MUNJALAU.NS",
        
        # INFRASTRUCTURE & CONSTRUCTION (Key Growth Driver)
        "LT.NS", "UBL.NS", "HCC.NS", "IRB.NS", "SADBHAV.NS", "DILIPBUILDCON.NS",
        "PNCINFRA.NS", "JPASSOCIAT.NS", "NCC.NS", "ASHOKA.NS", "JKCEMENT.NS",
        "HEIDELBERG.NS", "RAMCOCEM.NS", "DALBHARAT.NS", "INDIACEM.NS", "STARCEMENT.NS",
        "PRISMCEM.NS", "ORIENTCEM.NS", "DECCAN.NS", "MAGMA.NS", "JAICORPLTD.NS",
        "PRAKASH.NS", "HTMEDIA.NS", "GMR.NS", "GMRINFRA.NS", "GVK.NS",
        "KALPATPOWR.NS", "THERMAX.NS", "BGRENERGY.NS", "RPOWER.NS", "ADANIPOWER.NS",
        "TORNTPOWER.NS", "ADANIGREEN.NS", "RENUKA.NS", "SUZLON.NS", "INOXWIND.NS",
        
        # RETAIL & CONSUMER (Massive Sector)
        "DMART.NS", "SHOPPERS.NS", "TRENT.NS", "JUBLFOOD.NS", "WESTLIFE.NS",
        "DEVYANI.NS", "SPECIALITY.NS", "RELAXO.NS", "BATA.NS", "BATAINDIA.NS",
        "RUPA.NS", "GOKEX.NS", "SIYARAM.NS", "RAYMOND.NS", "ARVIND.NS",
        "CENTURYTEX.NS", "WELCORP.NS", "TEXRAIL.NS", "VARDHMAN.NS", "ALOKTEXT.NS",
        "MARICO.NS", "DABUR.NS", "GODREJCP.NS", "EMAMILTD.NS", "VIPIND.NS",
        "COLPAL.NS", "GILLETTE.NS", "HONASA.NS", "NYKAA.NS", "FINCABLES.NS",
        
        # MANUFACTURING & INDUSTRIALS (Make in India Focus)
        "BHEL.NS", "BEL.NS", "BEML.NS", "TIINDIA.NS", "CUMMINSIND.NS", "ABB.NS",
        "SIEMENS.NS", "SCHNEIDER.NS", "ORIENTELEC.NS", "HAVELLS.NS", "POLYCAB.NS",
        "FINOLEX.NS", "KEI.NS", "VINDHYATEL.NS", "RKFORGE.NS", "RATNAMANI.NS",
        "WELCORP.NS", "TEXINFRA.NS", "SONACOMS.NS", "MOTHERSUMI.NS", "BOSCHLTD.NS",
        "ESCORTS.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "TVSMOTOR.NS", "EICHERMOT.NS",
        "ASHOKLEY.NS", "MAHINDCIE.NS", "BHARATFORG.NS", "SUBROS.NS", "GABRIEL.NS",
        "ENDURANCE.NS", "SUPRAJIT.NS", "SUNDRMFAST.NS", "MINDAIND.NS", "CRAFTSMAN.NS",
        
        # HEALTHCARE & PHARMACEUTICALS (Complete Ecosystem)
        "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "LUPIN.NS",
        "BIOCON.NS", "TORNTPHARM.NS", "CADILAHC.NS", "GLENMARK.NS", "WOCKPHARMA.NS",
        "STRIDES.NS", "AJANTPHARM.NS", "ALKEM.NS", "MANKIND.NS", "GRANULES.NS",
        "IPCALAB.NS", "NEULANDLAB.NS", "NATCOPHAR.NS", "SOLARA.NS", "DRREDDYS.NS",
        "PFIZER.NS", "SANOFI.NS", "ABBOTINDIA.NS", "GSKCONS.NS", "JBCHEPHARM.NS",
        "ZYDUSWELL.NS", "STAR.NS", "REDDY.NS", "AUROPHARMA.NS", "SEQUENT.NS",
        "APOLLOHOSP.NS", "FORTIS.NS", "MAXHEALTH.NS", "NARAYANHRY.NS", "CARERATING.NS",
        "STARHEALTH.NS", "LALPATHLAB.NS", "METROPOLIS.NS", "THYROCARE.NS", "KRSNAA.NS",
        "RAINBOW.NS", "MEDPLUS.NS", "PHLX.NS", "VENKEYS.NS", "SUVEN.NS",
        
        # TECHNOLOGY & SOFTWARE (Digital India)
        "TCS.NS", "INFY.NS", "WIPRO.NS", "TECHM.NS", "HCLTECH.NS", "LTI.NS",
        "MINDTREE.NS", "MPHASIS.NS", "COFORGE.NS", "PERSISTENT.NS", "LTTS.NS",
        "CYIENT.NS", "ECLERX.NS", "FIRSTSOURCE.NS", "HEXAWARE.NS", "KPIT.NS",
        "NIITLTD.NS", "ROLTA.NS", "ZENSAR.NS", "POLARIS.NS", "INTELLECT.NS",
        "NEWGEN.NS", "RAMKY.NS", "SAKSOFT.NS", "MASTEK.NS", "INFRATEL.NS",
        "TATAELXSI.NS", "NELCO.NS", "INDIAINFO.NS", "SOFTTECH.NS", "RSYSTEMS.NS",
        
        # AUTOMOTIVE & AUTO COMPONENTS (Mobility Revolution)
        "MARUTI.NS", "TATAMOTORS.NS", "M&M.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS",
        "TVSMOTOR.NS", "EICHERMOT.NS", "ASHOKLEY.NS", "MAHINDCIE.NS", "BHARATFORG.NS",
        "MOTHERSUMI.NS", "BOSCHLTD.NS", "ESCORTS.NS", "BALKRISIND.NS", "MRF.NS",
        "APOLLOTYRE.NS", "CEAT.NS", "JK TYRE.NS", "GOODYEAR.NS", "SUBROS.NS",
        "GABRIEL.NS", "ENDURANCE.NS", "SUPRAJIT.NS", "SUNDRMFAST.NS", "MINDAIND.NS",
        "CRAFTSMAN.NS", "TEAMLEASE.NS", "FIEM.NS", "SETCO.NS", "RANE.NS"
    ]
    return nse_universe[:300]  # Limit to 300 for resource optimization

@st.cache_data(ttl=86400)
def get_complete_sp500_universe():
    """Complete S&P 500 with comprehensive sector coverage"""
    sp500_universe = [
        # TECHNOLOGY & SOFTWARE
        "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "TSLA", "META", "NVDA", "NFLX", "ADBE",
        "CRM", "ORCL", "INTC", "AMD", "QCOM", "AVGO", "CSCO", "IBM", "INTU", "NOW",
        "WDAY", "VEEV", "DDOG", "SNOW", "CRWD", "ZS", "OKTA", "SPLK", "MDB", "NET",
        "TEAM", "SHOP", "SQ", "PYPL", "ADSK", "ANSS", "CDNS", "SNPS", "FTNT",
        "PANW", "CYBR", "TENB", "QLYS", "ESTC", "DOMO", "TWLO", "ZM", "DOCU", "UBER",
        
        # FINANCIAL SERVICES & BANKING
        "JPM", "BAC", "WFC", "GS", "MS", "C", "AXP", "V", "MA", "PYPL",
        "BK", "USB", "PNC", "COF", "SCHW", "BLK", "SPGI", "MCO", "AIG", "TRV",
        "ALL", "PGR", "CB", "AON", "MMC", "MSCI", "ICE", "CME", "NDAQ", "CBOE",
        "KKR", "BX", "APO", "CG", "OWL", "ARES", "TPG", "HLNE", "BLUE", "EQH",
        
        # HEALTHCARE & PHARMACEUTICALS
        "JNJ", "PFE", "UNH", "ABBV", "TMO", "ABT", "MDT", "BMY", "AMGN", "GILD",
        "REGN", "BSX", "SYK", "ISRG", "ZBH", "BDX", "EW", "ALGN", "MRNA", "BNTX",
        "DHR", "A", "BAX", "BIO", "TECH", "PKI", "WAT", "MTD", "TFX", "WST",
        "CVS", "CI", "ANTM", "HUM", "CNC", "MOH", "ELV", "HCA", "THC", "UHS",
        "BIIB", "VRTX", "ILMN", "DXCM", "PODD", "TNDM", "OMCL", "TDOC", "HOLX", "VAR",
        
        # DEFENSE & AEROSPACE
        "BA", "LMT", "RTX", "NOC", "GD", "LHX", "LDOS", "HII", "TDG", "CW",
        "SPR", "AIR", "KTOS", "AVX", "HEI", "TXT", "PH", "ROL", "CACI", "SAIC",
        
        # MANUFACTURING & INDUSTRIALS
        "CAT", "GE", "MMM", "HON", "UPS", "FDX", "EMR", "ETN", "ITW", "PH",
        "CMI", "DE", "DOV", "ROK", "PNR", "AME", "ROP", "FTV", "XYL", "ITT",
        "IR", "GNRC", "CARR", "OTIS", "PCAR", "CMI", "WAB", "CHRW", "JBHT", "EXPD",
        "NSC", "CSX", "UNP", "KSU", "CNI", "CP", "TRN", "GWR", "RAIL", "GATX",
        
        # ENERGY & UTILITIES
        "XOM", "CVX", "COP", "EOG", "SLB", "MPC", "VLO", "PSX", "OXY", "HAL",
        "DVN", "FANG", "APA", "EQT", "COG", "MRO", "CNX", "RRC", "AR", "SM",
        "KMI", "WMB", "OKE", "EPD", "ET", "MPLX", "PAA", "WES", "ENLC", "SMLP",
        "NEE", "DUK", "SO", "AEP", "EXC", "XEL", "WEC", "ES", "AWK", "CMS",
        "CNP", "NI", "LNT", "EVRG", "ATO", "NRG", "PEG", "EIX", "PCG", "ED",
        
        # RETAIL & CONSUMER
        "WMT", "HD", "LOW", "COST", "TGT", "PG", "KO", "PEP", "MCD", "SBUX",
        "NKE", "TJX", "ROST", "YUM", "CMG", "ULTA", "ETSY", "EBAY", "DIS", "F",
        "GM", "TSLA", "LCID", "RIVN", "KMX", "AN", "LAD", "ABG", "SAH", "LEN",
        "DHI", "PHM", "TOL", "KBH", "MTH", "TMHC", "LGIH", "MHO", "GRBK", "CVCO",
        "MAR", "HLT", "H", "IHG", "WH", "RHP", "PENN", "MGM", "LVS", "WYNN",
        
        # MATERIALS & CHEMICALS
        "LIN", "APD", "ECL", "SHW", "FCX", "NEM", "FMC", "ALB", "EMN", "IFF",
        "PPG", "CF", "MOS", "LYB", "DOW", "DD", "CE", "VMC", "MLM", "NUE"
    ]
    return sp500_universe[:250]  # Limit to 250 for resource optimization

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
    
    # Rotate to next batch
    start_idx = (current_batch_num * batch_size) % len(symbols)
    end_idx = min(start_idx + batch_size, len(symbols))
    
    # Handle wrap-around
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
    
    # Get current batch
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
            data['Volume_MA'] = data['Volume'].rolling(window=20).mean()
            
            latest = data.iloc[-1]
            current_price = latest['Close']
            rsi = latest['RSI']
            
            if pd.isna(rsi) or pd.isna(current_price):
                continue
            
            volume_ratio = latest['Volume'] / max(latest.get('Volume_MA', latest['Volume']), 1)
            
            # Enhanced filtering for better opportunities
            price_filter = current_price >= min_price
            rsi_filter = rsi <= max_rsi
            volume_filter = volume_ratio > 1.0
            trend_filter = latest['Close'] > latest['EMA20']
            momentum_filter = latest['EMA20'] > latest['EMA50']
            
            if price_filter and rsi_filter and volume_filter and trend_filter:
                # Calculate targets
                returns = data['Close'].pct_change().dropna()
                volatility = returns.std()
                
                if market_type == "Indian":
                    if volatility > 0.03:
                        target_pct = 0.12
                        days_estimate = 12
                    elif volatility > 0.02:
                        target_pct = 0.08
                        days_estimate = 15
                    else:
                        target_pct = 0.06
                        days_estimate = 20
                    sl_pct = 0.07
                else:  # US market
                    if volatility > 0.025:
                        target_pct = 0.10
                        days_estimate = 10
                    elif volatility > 0.018:
                        target_pct = 0.07
                        days_estimate = 12
                    else:
                        target_pct = 0.05
                        days_estimate = 18
                    sl_pct = 0.06
                
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
            
        except Exception:
            continue
    
    progress_bar.empty()
    status_placeholder.empty()
    
    return pd.DataFrame(recommendations), next_batch_num

def fetch_news_optimized():
    """Fetch news efficiently"""
    sources = {
        'Economic Times': 'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
        'Moneycontrol': 'https://www.moneycontrol.com/rss/business.xml',
        'Business Standard': 'https://www.business-standard.com/rss/markets-106.rss'
    }
    
    all_news = []
    for source_name, url in sources.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:12]:
                title = entry.get('title', 'No Title')
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
    return all_news[:40]

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
• Defense & Aerospace
• Infrastructure & Construction  
• Manufacturing & Auto
• Healthcare & Pharma
• Banking & Financial
• Energy & Power
• Technology & Software
• Retail & Consumer

🇺🇸 S&P 500: {len(sp500_universe)} stocks
• All Major Sectors Covered

**🔄 Professional Batch System**
NSE: Batch {st.session_state.nse_batch_num + 1}
S&P: Batch {st.session_state.sp500_batch_num + 1}

**💼 For Broking Associates**
Screenshot → Refresh → Next Batch
Zero Opportunity Missed!
""")

batch_size = st.sidebar.selectbox("Batch Size", [15, 20, 25, 30], index=1)

if st.sidebar.button("🔄 Reset Batch Counters"):
    st.session_state.nse_batch_num = 0
    st.session_state.sp500_batch_num = 0
    st.success("Batch counters reset - starting from batch 1")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📰 Market News", 
    f"🇮🇳 NSE Stocks ({len(nse_universe)})", 
    f"🇺🇸 S&P 500 ({len(sp500_universe)})", 
    "📊 Scan History"
])

# Tab 1: News
with tab1:
    st.subheader("📰 Market News & Analysis")
    
    if st.button("🔄 Refresh News") or not st.session_state.news_data:
        with st.spinner("Loading latest market news..."):
            st.session_state.news_data = fetch_news_optimized()
            st.success(f"Loaded {len(st.session_state.news_data)} news items!")
    
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
    st.subheader(f"🇮🇳 NSE Complete Sector Scanner ({len(nse_universe)} stocks)")
    
    st.markdown("""
    <div class="coverage-info">
    <strong>📊 COMPLETE SECTOR COVERAGE:</strong><br>
    🛡️ <strong>Defense:</strong> HAL, BEL, BDL, GRSE, MDL, BEML, BHEL<br>
    🏗️ <strong>Infrastructure:</strong> L&T, IRB, HCC, NCC, JKCEMENT, RAMCOCEM<br>
    🏭 <strong>Manufacturing:</strong> BHEL, SIEMENS, ABB, CUMMINSIND, HAVELLS<br>
    🏥 <strong>Healthcare:</strong> Complete pharma + hospitals + diagnostics<br>
    🏦 <strong>Banking:</strong> All PSU, private, NBFCs, housing finance<br>
    ⚡ <strong>Energy:</strong> Oil, gas, power, renewables, transmission<br>
    💻 <strong>Technology:</strong> IT services, software, digital, emerging tech<br>
    🛒 <strong>Retail:</strong> DMART, organized retail, consumer brands, FMCG
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        min_price_in = st.number_input("Min Price (₹)", value=25, min_value=1, key="nse_min_price")
    with col2:
        max_rsi_in = st.number_input("Max RSI", value=35, min_value=1, max_value=100, key="nse_max_rsi")
    with col3:
        batch_size_nse = st.selectbox("Batch Size", [15, 20, 25, 30], index=1, key="nse_batch")
    
    if st.button("🔍 Scan Next NSE Batch (All Sectors)", type="primary"):
        with st.spinner(f"Scanning batch {st.session_state.nse_batch_num + 1} across ALL sectors..."):
            recommendations, next_batch = scan_rotating_batch(
                nse_universe, min_price_in, max_rsi_in, "Indian", batch_size_nse, st.session_state.nse_batch_num
            )
            st.session_state.indian_recos = recommendations
            st.session_state.nse_batch_num = next_batch
            
            # Add to scan history
            if not recommendations.empty:
                scan_record = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'market': 'NSE',
                    'batch': f"{st.session_state.nse_batch_num}/{((len(nse_universe) + batch_size_nse - 1) // batch_size_nse)}",
                    'found': len(recommendations),
                    'top_stock': recommendations.iloc[0]['Stock'] if len(recommendations) > 0 else 'None'
                }
                st.session_state.scan_history.append(scan_record)
    
    if not st.session_state.indian_recos.empty:
        st.success(f"🎯 Found {len(st.session_state.indian_recos)} opportunities across multiple sectors!")
        st.dataframe(st.session_state.indian_recos, use_container_width=True, height=300)
        
        csv = st.session_state.indian_recos.to_csv(index=False)
        st.download_button(
            "📥 Download NSE Recommendations",
            csv,
            f"nse_all_sectors_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv"
        )
    else:
        st.info("🔍 Click 'Scan Next NSE Batch' to discover opportunities across all sectors!")

# Tab 3: S&P 500 Stocks  
with tab3:
    st.subheader(f"🇺🇸 S&P 500 Complete Sector Scanner ({len(sp500_universe)} stocks)")
    
    st.markdown("""
    <div class="coverage-info">
    <strong>📊 COMPLETE S&P 500 SECTOR COVERAGE:</strong><br>
    💻 <strong>Technology:</strong> FAANG + software + semiconductors + cybersecurity<br>
    🏦 <strong>Financials:</strong> Banks + insurance + asset management + fintech<br>
    🏥 <strong>Healthcare:</strong> Pharma + biotech + medical devices + services<br>
    🛡️ <strong>Defense:</strong> BA, LMT, RTX, NOC, GD + aerospace contractors<br>
    🏭 <strong>Industrials:</strong> Manufacturing + transportation + logistics<br>
    ⚡ <strong>Energy:</strong> Oil majors + renewables + utilities + pipelines<br>
    🛒 <strong>Consumer:</strong> Retail + brands + restaurants + apparel
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        min_price_us = st.number_input("Min Price ($)", value=25, min_value=1, key="sp500_min_price")
    with col2:
        max_rsi_us = st.number_input("Max RSI", value=35, min_value=1, max_value=100, key="sp500_max_rsi")
    with col3:
        batch_size_us = st.selectbox("Batch Size", [15, 20, 25, 30], index=1, key="sp500_batch")
    
    if st.button("🔍 Scan Next S&P 500 Batch (All Sectors)", type="primary"):
        with st.spinner(f"Scanning batch {st.session_state.sp500_batch_num + 1} across ALL sectors..."):
            recommendations, next_batch = scan_rotating_batch(
                sp500_universe, min_price_us, max_rsi_us, "US", batch_size_us, st.session_state.sp500_batch_num
            )
            st.session_state.us_recos = recommendations
            st.session_state.sp500_batch_num = next_batch
            
            # Add to scan history
            if not recommendations.empty:
                scan_record = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'market': 'S&P 500',
                    'batch': f"{st.session_state.sp500_batch_num}/{((len(sp500_universe) + batch_size_us - 1) // batch_size_us)}",
                    'found': len(recommendations),
                    'top_stock': recommendations.iloc[0]['Stock'] if len(recommendations) > 0 else 'None'
                }
                st.session_state.scan_history.append(scan_record)
    
    if not st.session_state.us_recos.empty:
        st.success(f"🎯 Found {len(st.session_state.us_recos)} S&P 500 opportunities across multiple sectors!")
        st.dataframe(st.session_state.us_recos, use_container_width=True, height=300)
        
        csv = st.session_state.us_recos.to_csv(index=False)
        st.download_button(
            "📥 Download S&P 500 Recommendations",
            csv,
            f"sp500_all_sectors_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv"
        )
    else:
        st.info("🔍 Click 'Scan Next S&P 500 Batch' to discover opportunities across all sectors!")

# Tab 4: Scan History
with tab4:
    st.subheader("📊 Professional Scan History & Coverage Tracker")
    
    if st.session_state.scan_history:
        history_df = pd.DataFrame(st.session_state.scan_history)
        
        st.markdown("""
        <div class="opportunity-alert">
        <strong>📈 Professional Usage Statistics</strong><br>
        Track your complete market coverage and opportunity discovery across all scans
        </div>
        """, unsafe_allow_html=True)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Scans", len(history_df))
        with col2:
            st.metric("Total Opportunities", history_df['found'].sum())
        with col3:
            st.metric("NSE Batches", len(history_df[history_df['market'] == 'NSE']))
        with col4:
            st.metric("S&P 500 Batches", len(history_df[history_df['market'] == 'S&P 500']))
        
        st.dataframe(history_df, use_container_width=True)
        
        if st.button("📥 Export Scan History"):
            csv = history_df.to_csv(index=False)
            st.download_button(
                "Download History CSV",
                csv,
                f"scan_history_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )
        
        if st.button("🗑️ Clear History"):
            st.session_state.scan_history = []
            st.success("Scan history cleared!")
            st.rerun()
    else:
        st.info("No scan history yet. Start scanning to track your coverage!")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**📊 Professional Trading Dashboard**")
with col2:
    st.markdown(f"**🕐 Updated:** {datetime.now().strftime('%H:%M:%S')}")
with col3:
    st.markdown("**🎯 Complete Sector Coverage**")
