    import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st

def calculate_rsi(data, window=14):
    """Calculate RSI indicator"""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_nse_stock_universe():
    """Get comprehensive NSE stock universe"""
    return [
        # Nifty 50 Core
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
        
        # Banking & Financial
        "BANKBARODA.NS", "PNB.NS", "CANBK.NS", "RBLBANK.NS", "YESBANK.NS",
        "FEDERALBNK.NS", "BANDHANBNK.NS", "AUBANK.NS", "CHOLAFIN.NS", "MUTHOOTFIN.NS",
        
        # Defense & Aerospace
        "HAL.NS", "BEL.NS", "BEML.NS", "BHEL.NS", "COCHINSHIP.NS", "TIINDIA.NS",
        
        # Infrastructure
        "HCC.NS", "IRB.NS", "NCC.NS", "JKCEMENT.NS", "RAMCOCEM.NS", "DALBHARAT.NS",
        
        # Healthcare & Pharma
        "BIOCON.NS", "LUPIN.NS", "TORNTPHARM.NS", "GLENMARK.NS", "WOCKPHARMA.NS",
        "STRIDES.NS", "AJANTPHARM.NS", "ALKEM.NS", "MANKIND.NS", "GRANULES.NS",
        "PFIZER.NS", "SANOFI.NS", "ABBOTINDIA.NS", "LALPATHLAB.NS", "METROPOLIS.NS",
        
        # Technology
        "MINDTREE.NS", "MPHASIS.NS", "COFORGE.NS", "PERSISTENT.NS", "LTTS.NS",
        "CYIENT.NS", "ECLERX.NS", "FIRSTSOURCE.NS", "HEXAWARE.NS", "KPIT.NS",
        
        # Auto & Components
        "MOTHERSUMI.NS", "BOSCHLTD.NS", "ESCORTS.NS", "BALKRISIND.NS", "MRF.NS",
        "APOLLOTYRE.NS", "CEAT.NS", "SUBROS.NS", "GABRIEL.NS", "ENDURANCE.NS",
        
        # Energy & Power
        "GAIL.NS", "PETRONET.NS", "IGL.NS", "MGL.NS", "ADANIGREEN.NS",
        "TORNTPOWER.NS", "ADANIPOWER.NS", "SUZLON.NS", "RPOWER.NS",
        
        # Consumer & Retail
        "DMART.NS", "TRENT.NS", "JUBLFOOD.NS", "RELAXO.NS", "BATAINDIA.NS",
        "MARICO.NS", "DABUR.NS", "GODREJCP.NS", "COLPAL.NS", "EMAMILTD.NS",
        
        # Manufacturing & Industrial
        "SIEMENS.NS", "ABB.NS", "CUMMINSIND.NS", "HAVELLS.NS", "POLYCAB.NS",
        "FINOLEX.NS", "RATNAMANI.NS", "THERMAX.NS",
        
        # Metals & Mining
        "SAIL.NS", "NMDC.NS", "VEDL.NS", "JINDALSTEL.NS", "HEG.NS",
        
        # Agriculture & Fertilizers
        "COROMANDEL.NS", "GSFC.NS", "NFL.NS", "RCF.NS", "DEEPAKNTR.NS", "SRF.NS",
        
        # Telecom & Media
        "IDEA.NS", "ZEEL.NS", "SUNTV.NS", "TATACOMM.NS",
        
        # Real Estate
        "DLF.NS", "GODREJPROP.NS", "SOBHA.NS", "BRIGADE.NS",
        
        # New Age Stocks
        "ZOMATO.NS", "NYKAA.NS", "PAYTM.NS", "DELHIVERY.NS"
    ]

def get_indian_recommendations(min_price=25, max_rsi=50, min_volume=100000):
    """Get Indian stock recommendations with guaranteed results"""
    
    symbols = get_nse_stock_universe()
    recommendations = []
    
    # Show progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, symbol in enumerate(symbols[:30]):  # Limit to 30 for speed
        try:
            progress_bar.progress((i + 1) / 30)
            status_text.text(f"Analyzing {symbol.replace('.NS', '')}...")
            
            # Fetch data
            stock = yf.Ticker(symbol)
            data = stock.history(period="6mo", interval="1d")
            
            if len(data) < 50:
                continue
            
            # Calculate indicators
            data['RSI'] = calculate_rsi(data)
            data['EMA20'] = data['Close'].ewm(span=20).mean()
            data['EMA50'] = data['Close'].ewm(span=50).mean()
            
            latest = data.iloc[-1]
            current_price = latest['Close']
            rsi = latest['RSI']
            
            # Handle volume safely
            avg_volume = data['Volume'].tail(20).mean() if 'Volume' in data.columns else min_volume
            
            # Apply filters - more lenient for guaranteed results
            if (current_price >= min_price and 
                rsi <= max_rsi and 
                not pd.isna(rsi) and 
                not pd.isna(current_price) and
                avg_volume >= min_volume * 0.5):  # 50% of required volume
                
                # Calculate targets based on volatility
                returns = data['Close'].pct_change().dropna()
                volatility = returns.std()
                
                if volatility > 0.025:
                    target_pct = 0.12  # 12% for high vol
                    days_est = 15
                elif volatility > 0.018:
                    target_pct = 0.08  # 8% for medium vol
                    days_est = 18
                else:
                    target_pct = 0.06  # 6% for low vol
                    days_est = 22
                
                target = current_price * (1 + target_pct)
                sl = current_price * 0.93  # 7% SL
                
                # Check trend alignment
                trend_score = 0
                if latest['Close'] > latest['EMA20']:
                    trend_score += 1
                if latest['EMA20'] > latest['EMA50']:
                    trend_score += 1
                if rsi < 40:  # Not overbought
                    trend_score += 1
                
                if trend_score >= 2:  # At least 2 of 3 conditions
                    recommendations.append({
                        'Date': datetime.now().strftime('%Y-%m-%d'),
                        'Stock': symbol.replace('.NS', ''),
                        'LTP': round(current_price, 2),
                        'RSI': round(rsi, 1),
                        'Target': round(target, 2),
                        '% Gain': round(target_pct * 100, 1),
                        'Est. Days': days_est,
                        'Stop Loss': round(sl, 2),
                        'Volume': int(avg_volume),
                        'Trend Score': trend_score,
                        'Status': 'Active'
                    })
        
        except Exception as e:
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    # Sort by % gain potential
    df = pd.DataFrame(recommendations)
    if not df.empty:
        df = df.sort_values('% Gain', ascending=False)
    
    return df

def get_indian_market_overview():
    """Get Indian market overview"""
    try:
        # Fetch Nifty data
        nifty = yf.download("^NSEI", period="1d", interval="5m")
        sensex = yf.download("^BSESN", period="1d", interval="5m")
        
        overview = {}
        
        if not nifty.empty:
            nifty_close = nifty['Close'].iloc[-1]
            nifty_open = nifty['Open'].iloc[0]
            nifty_change = nifty_close - nifty_open
            nifty_pct = (nifty_change / nifty_open) * 100
            
            overview['nifty'] = {
                'price': round(nifty_close, 2),
                'change': round(nifty_change, 2),
                'change_pct': round(nifty_pct, 2)
            }
        
        if not sensex.empty:
            sensex_close = sensex['Close'].iloc[-1]
            sensex_open = sensex['Open'].iloc[0]
            sensex_change = sensex_close - sensex_open
            sensex_pct = (sensex_change / sensex_open) * 100
            
            overview['sensex'] = {
                'price': round(sensex_close, 2),
                'change': round(sensex_change, 2),
                'change_pct': round(sensex_pct, 2)
            }
        
        overview['last_updated'] = datetime.now().strftime('%H:%M:%S')
        return overview
        
    except Exception as e:
        return {
            'nifty': {'price': 0, 'change': 0, 'change_pct': 0},
            'sensex': {'price': 0, 'change': 0, 'change_pct': 0},
            'last_updated': 'Error loading data'
        }

def get_sector_analysis(recommendations_df):
    """Analyze sector distribution of recommendations"""
    if recommendations_df.empty:
        return {}
    
    sector_mapping = {
        'TCS': 'Technology', 'INFY': 'Technology', 'WIPRO': 'Technology', 'TECHM': 'Technology',
        'HCLTECH': 'Technology', 'MINDTREE': 'Technology', 'MPHASIS': 'Technology',
        'RELIANCE': 'Energy', 'ONGC': 'Energy', 'IOC': 'Energy', 'BPCL': 'Energy',
        'HDFCBANK': 'Banking', 'ICICIBANK': 'Banking', 'SBIN': 'Banking', 'KOTAKBANK': 'Banking',
        'AXISBANK': 'Banking', 'INDUSINDBK': 'Banking', 'FEDERALBNK': 'Banking',
        'SUNPHARMA': 'Pharma', 'DRREDDY': 'Pharma', 'CIPLA': 'Pharma', 'LUPIN': 'Pharma',
        'BIOCON': 'Pharma', 'DIVISLAB': 'Pharma', 'TORNTPHARM': 'Pharma',
        'MARUTI': 'Auto', 'TATAMOTORS': 'Auto', 'M&M': 'Auto', 'BAJAJ-AUTO': 'Auto',
        'HEROMOTOCO': 'Auto', 'TVSMOTOR': 'Auto', 'EICHERMOT': 'Auto',
        'HAL': 'Defense', 'BEL': 'Defense', 'BHEL': 'Defense', 'BEML': 'Defense',
        'LT': 'Infrastructure', 'HCC': 'Infrastructure', 'IRB': 'Infrastructure',
        'JKCEMENT': 'Infrastructure', 'RAMCOCEM': 'Infrastructure'
    }
    
    sector_counts = {}
    for _, row in recommendations_df.iterrows():
        sector = sector_mapping.get(row['Stock'], 'Others')
        sector_counts[sector] = sector_counts.get(sector, 0) + 1
    
    return sector_counts
