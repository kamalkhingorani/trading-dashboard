import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

def calculate_rsi(data, window=14):
    """Calculate RSI indicator"""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_dynamic_targets(data, current_price):
    """Calculate dynamic targets based on multiple factors"""
    
    # Historical volatility (20-day)
    returns = data['Close'].pct_change().dropna()
    volatility = returns.tail(20).std() * np.sqrt(252)  # Annualized
    
    # Recent price range (support/resistance)
    recent_data = data.tail(30)
    resistance = recent_data['High'].max()
    support = recent_data['Low'].min()
    
    # Moving average distances
    sma20 = data['Close'].rolling(20).mean().iloc[-1]
    sma50 = data['Close'].rolling(50).mean().iloc[-1]
    
    # Volume trend
    avg_volume = data['Volume'].tail(20).mean() if 'Volume' in data.columns else 100000
    recent_volume = data['Volume'].iloc[-1] if 'Volume' in data.columns else avg_volume
    volume_surge = recent_volume > (avg_volume * 1.2)
    
    # Base target calculation
    if volatility > 0.35:  # High volatility stock
        base_target_pct = np.random.uniform(0.08, 0.15)  # 8-15%
        days_range = (12, 25)
    elif volatility > 0.25:  # Medium volatility
        base_target_pct = np.random.uniform(0.05, 0.12)  # 5-12%
        days_range = (15, 30)
    else:  # Low volatility
        base_target_pct = np.random.uniform(0.03, 0.08)  # 3-8%
        days_range = (20, 35)
    
    # Adjust based on technical factors
    if current_price > sma20 > sma50:  # Strong uptrend
        base_target_pct *= 1.2
        days_range = (days_range[0]-3, days_range[1]-5)
    
    if volume_surge:  # High volume suggests strong move
        base_target_pct *= 1.1
    
    # Resistance-based target
    resistance_target_pct = (resistance - current_price) / current_price
    
    # Use the more conservative of the two
    final_target_pct = min(base_target_pct, resistance_target_pct * 0.8)
    final_target_pct = max(final_target_pct, 0.02)  # Minimum 2%
    
    target_price = current_price * (1 + final_target_pct)
    estimated_days = np.random.randint(days_range[0], days_range[1])
    
    # Stop loss based on support
    support_sl_pct = (current_price - support) / current_price
    volatility_sl_pct = volatility * 0.3  # 30% of annual volatility
    
    sl_pct = min(support_sl_pct * 0.8, volatility_sl_pct, 0.12)  # Max 12% SL
    sl_pct = max(sl_pct, 0.05)  # Minimum 5% SL
    
    stop_loss = current_price * (1 - sl_pct)
    
    return {
        'target': target_price,
        'target_pct': final_target_pct * 100,
        'stop_loss': stop_loss,
        'estimated_days': estimated_days,
        'volatility': volatility,
        'volume_surge': volume_surge
    }

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

def get_indian_recommendations(min_price=25, max_rsi=60, min_volume=100000, batch_size=30):
    """Get Indian stock recommendations with dynamic targets"""
    
    symbols = get_nse_stock_universe()
    recommendations = []
    
    # Show progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Batch processing for memory management
    total_symbols = min(len(symbols), batch_size)
    
    for i, symbol in enumerate(symbols[:total_symbols]):
        try:
            progress_bar.progress((i + 1) / total_symbols)
            status_text.text(f"Analyzing {symbol.replace('.NS', '')}... ({i+1}/{total_symbols})")
            
            # Fetch data
            stock = yf.Ticker(symbol)
            data = stock.history(period="6mo", interval="1d")
            
            if len(data) < 50:
                continue
            
            # Calculate indicators
            data['RSI'] = calculate_rsi(data)
            data['EMA20'] = data['Close'].ewm(span=20).mean()
            data['EMA50'] = data['Close'].ewm(span=50).mean()
            data['SMA20'] = data['Close'].rolling(20).mean()
            
            # MACD
            exp1 = data['Close'].ewm(span=12).mean()
            exp2 = data['Close'].ewm(span=26).mean()
            data['MACD'] = exp1 - exp2
            data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
            
            latest = data.iloc[-1]
            current_price = latest['Close']
            rsi = latest['RSI']
            
            # Handle volume safely
            avg_volume = data['Volume'].tail(20).mean() if 'Volume' in data.columns else min_volume
            
            # Apply filters
            if (current_price >= min_price and 
                rsi <= max_rsi and 
                not pd.isna(rsi) and 
                not pd.isna(current_price) and
                avg_volume >= min_volume * 0.5):
                
                # Calculate dynamic targets
                target_data = calculate_dynamic_targets(data, current_price)
                
                # Technical score calculation
                technical_score = 0
                
                # Trend alignment
                if latest['Close'] > latest['EMA20']:
                    technical_score += 1
                if latest['EMA20'] > latest['EMA50']:
                    technical_score += 1
                
                # RSI conditions
                if 30 <= rsi <= 60:  # Good RSI range
                    technical_score += 1
                
                # MACD signal
                if latest['MACD'] > latest['MACD_Signal']:
                    technical_score += 1
                
                # Volume confirmation
                if target_data['volume_surge']:
                    technical_score += 1
                
                # Only include stocks with good technical score
                if technical_score >= 3:  # At least 3 of 5 conditions
                    
                    # Risk rating based on volatility
                    if target_data['volatility'] > 0.35:
                        risk_rating = 'High'
                    elif target_data['volatility'] > 0.25:
                        risk_rating = 'Medium'
                    else:
                        risk_rating = 'Low'
                    
                    recommendations.append({
                        'Date': datetime.now().strftime('%Y-%m-%d'),
                        'Stock': symbol.replace('.NS', ''),
                        'LTP': round(current_price, 2),
                        'RSI': round(rsi, 1),
                        'Target': round(target_data['target'], 2),
                        '% Gain': round(target_data['target_pct'], 1),
                        'Est. Days': target_data['estimated_days'],
                        'Stop Loss': round(target_data['stop_loss'], 2),
                        'SL %': round(target_data['sl_pct'], 1),
                        'Risk:Reward': f"1:{target_data['risk_reward_ratio']}",
                        'Volume': int(avg_volume),
                        'Risk': risk_rating,
                        'Tech Score': f"{technical_score}/5",
                        'Volatility': f"{target_data['volatility']:.1%}",
                        'Status': 'Active'
                    })
        
        except Exception as e:
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    # Sort by technical score and then by % gain potential
    df = pd.DataFrame(recommendations)
    if not df.empty:
        df = df.sort_values(['Tech Score', '% Gain'], ascending=[False, False])
    
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
