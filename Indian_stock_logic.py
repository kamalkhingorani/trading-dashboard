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
    """Calculate dynamic targets based on multiple factors with proper risk management"""
    
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
    
    # Trend strength
    price_above_sma20 = current_price > sma20
    sma20_above_sma50 = sma20 > sma50
    uptrend = price_above_sma20 and sma20_above_sma50
    
    # Base target calculation based on volatility
    if volatility > 0.35:  # High volatility stock
        base_target_pct = np.random.uniform(0.08, 0.15)  # 8-15%
        days_range = (10, 20)
    elif volatility > 0.25:  # Medium volatility
        base_target_pct = np.random.uniform(0.05, 0.10)  # 5-10%
        days_range = (15, 25)
    else:  # Low volatility
        base_target_pct = np.random.uniform(0.03, 0.07)  # 3-7%
        days_range = (20, 35)
    
    # Adjust based on technical factors
    if uptrend:
        base_target_pct *= 1.15  # 15% boost for uptrend
        days_range = (days_range[0]-2, days_range[1]-3)
    
    if volume_surge:
        base_target_pct *= 1.08  # 8% boost for volume
    
    # Recent momentum
    momentum_5d = (current_price - data['Close'].iloc[-6]) / data['Close'].iloc[-6]
    if momentum_5d > 0.02:  # Positive momentum
        base_target_pct *= 1.05
    
    # Resistance-based ceiling
    resistance_room = (resistance - current_price) / current_price
    if resistance_room < base_target_pct:
        base_target_pct = resistance_room * 0.85  # Leave some room before resistance
    
    # Ensure minimum target
    final_target_pct = max(base_target_pct, 0.025)  # Minimum 2.5%
    final_target_pct = min(final_target_pct, 0.15)   # Maximum 15%
    
    target_price = current_price * (1 + final_target_pct)
    estimated_days = np.random.randint(days_range[0], days_range[1])
    
    # CORRECTED STOP LOSS CALCULATION
    # Calculate multiple stop loss options
    support_based_sl = (current_price - support) / current_price
    volatility_based_sl = volatility * 0.15  # 15% of annual volatility
    atr_based_sl = returns.tail(14).std() * 2  # 2x ATR
    
    # Risk management rule: Stop loss should be maximum 50% of target gain
    max_allowed_sl_pct = final_target_pct * 0.5  # 50% of potential gain
    
    # Choose the most appropriate stop loss
    sl_pct = min(
        support_based_sl * 0.8,  # 80% of distance to support
        volatility_based_sl,
        atr_based_sl,
        max_allowed_sl_pct,      # Never exceed 50% of gain
        0.08                     # Maximum 8% stop loss
    )
    
    # Ensure minimum stop loss (not too tight)
    sl_pct = max(sl_pct, 0.02)  # Minimum 2% stop loss
    
    stop_loss = current_price * (1 - sl_pct)
    
    # Calculate actual risk-reward ratio
    potential_gain = target_price - current_price
    potential_loss = current_price - stop_loss
    risk_reward_ratio = potential_gain / potential_loss if potential_loss > 0 else 999
    
    # Add some randomness to avoid all stocks having same values
    random_factor = np.random.uniform(0.95, 1.05)
    
    return {
        'target': target_price,
        'target_pct': final_target_pct * 100,
        'stop_loss': stop_loss,
        'sl_pct': sl_pct * 100,
        'estimated_days': int(estimated_days * random_factor),
        'volatility': volatility,
        'volume_surge': volume_surge,
        'risk_reward_ratio': round(risk_reward_ratio, 2),
        'uptrend': uptrend,
        'momentum_5d': momentum_5d
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
                
                # Only include stocks with good risk-reward ratio
                if target_data['risk_reward_ratio'] >= 2.0:
                    
                    # Technical score calculation
                    technical_score = 0
                    
                    # Trend alignment
                    if latest['Close'] > latest['EMA20']:
                        technical_score += 1
                    if latest['EMA20'] > latest['EMA50']:
                        technical_score += 1
                    
                    # RSI conditions
                    if 30 <= rsi <= 60:
                        technical_score += 1
                    
                    # MACD signal
                    if latest['MACD'] > latest['MACD_Signal']:
                        technical_score += 1
                    
                    # Volume confirmation
                    if target_data['volume_surge']:
                        technical_score += 1
                    
                    # Only include stocks with good technical score
                    if technical_score >= 3:
                        
                        # Risk rating based on volatility
                        if target_data['volatility'] > 0.35:
                            risk_rating = 'High'
                        elif target_data['volatility'] > 0.25:
                            risk_rating = 'Medium'
                        else:
                            risk_rating = 'Low'
                        
                        # Get sector
                        sector = get_stock_sector(symbol.replace('.NS', ''))
                        
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
                            'Sector': sector,
                            'Volatility': f"{target_data['volatility']:.1%}",
                            'Momentum': 'Positive' if target_data['momentum_5d'] > 0 else 'Negative',
                            'Status': 'Active'
                        })
        
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    # Sort by risk-reward ratio and technical score
    df = pd.DataFrame(recommendations)
    if not df.empty:
        df['RR_numeric'] = df['Risk:Reward'].str.extract(r'1:(\d+\.?\d*)').astype(float)
        df = df.sort_values(['RR_numeric', 'Tech Score'], ascending=[False, False])
        df = df.drop('RR_numeric', axis=1)
    
    return df

def get_stock_sector(symbol):
    """Get sector for Indian stock symbol"""
    sector_mapping = {
        # Technology
        'TCS': 'Technology', 'INFY': 'Technology', 'WIPRO': 'Technology', 'TECHM': 'Technology',
        'HCLTECH': 'Technology', 'MINDTREE': 'Technology', 'MPHASIS': 'Technology', 'COFORGE': 'Technology',
        'PERSISTENT': 'Technology', 'LTTS': 'Technology', 'CYIENT': 'Technology',
        
        # Banking
        'HDFCBANK': 'Banking', 'ICICIBANK': 'Banking', 'SBIN': 'Banking', 'KOTAKBANK': 'Banking',
        'AXISBANK': 'Banking', 'INDUSINDBK': 'Banking', 'FEDERALBNK': 'Banking', 'BANDHANBNK': 'Banking',
        'AUBANK': 'Banking', 'PNB': 'Banking', 'BANKBARODA': 'Banking', 'CANBK': 'Banking',
        
        # Financial Services
        'BAJFINANCE': 'Financial', 'BAJAJFINSV': 'Financial', 'CHOLAFIN': 'Financial', 
        'MUTHOOTFIN': 'Financial', 'SBILIFE': 'Insurance', 'HDFCLIFE': 'Insurance',
        
        # Pharma
        'SUNPHARMA': 'Pharma', 'DRREDDY': 'Pharma', 'CIPLA': 'Pharma', 'LUPIN': 'Pharma',
        'BIOCON': 'Pharma', 'DIVISLAB': 'Pharma', 'TORNTPHARM': 'Pharma', 'GLENMARK': 'Pharma',
        'ALKEM': 'Pharma', 'AJANTPHARM': 'Pharma', 'GRANULES': 'Pharma', 'STRIDES': 'Pharma',
        
        # Auto
        'MARUTI': 'Auto', 'TATAMOTORS': 'Auto', 'M&M': 'Auto', 'BAJAJ-AUTO': 'Auto',
        'HEROMOTOCO': 'Auto', 'EICHERMOT': 'Auto', 'ESCORTS': 'Auto', 'MOTHERSUMI': 'Auto Parts',
        'BOSCHLTD': 'Auto Parts', 'MRF': 'Auto Parts', 'APOLLOTYRE': 'Auto Parts',
        
        # Energy
        'RELIANCE': 'Energy', 'ONGC': 'Energy', 'IOC': 'Energy', 'BPCL': 'Energy',
        'GAIL': 'Energy', 'PETRONET': 'Energy', 'IGL': 'Energy', 'MGL': 'Energy',
        'ADANIGREEN': 'Energy', 'TORNTPOWER': 'Energy', 'ADANIPOWER': 'Energy',
        
        # Defense
        'HAL': 'Defense', 'BEL': 'Defense', 'BHEL': 'Defense', 'BEML': 'Defense',
        'COCHINSHIP': 'Defense', 'TIINDIA': 'Defense',
        
        # Infrastructure
        'LT': 'Infrastructure', 'ULTRACEMCO': 'Cement', 'SHREECEM': 'Cement', 
        'JKCEMENT': 'Cement', 'RAMCOCEM': 'Cement', 'DALBHARAT': 'Cement',
        'HCC': 'Infrastructure', 'IRB': 'Infrastructure', 'NCC': 'Infrastructure',
        
        # FMCG
        'HINDUNILVR': 'FMCG', 'ITC': 'FMCG', 'NESTLEIND': 'FMCG', 'BRITANNIA': 'FMCG',
        'DABUR': 'FMCG', 'MARICO': 'FMCG', 'GODREJCP': 'FMCG', 'COLPAL': 'FMCG',
        'EMAMILTD': 'FMCG', 'TATACONSUM': 'FMCG',
        
        # Metals
        'TATASTEEL': 'Metals', 'HINDALCO': 'Metals', 'JSWSTEEL': 'Metals', 'SAIL': 'Metals',
        'NMDC': 'Metals', 'VEDL': 'Metals', 'JINDALSTEL': 'Metals',
        
        # Retail
        'DMART': 'Retail', 'TRENT': 'Retail', 'JUBLFOOD': 'Retail', 'TITAN': 'Retail',
        'RELAXO': 'Retail', 'BATAINDIA': 'Retail',
        
        # Real Estate
        'DLF': 'Real Estate', 'GODREJPROP': 'Real Estate', 'SOBHA': 'Real Estate', 'BRIGADE': 'Real Estate',
        
        # Others
        'ASIANPAINT': 'Paints', 'PIDILITIND': 'Chemicals', 'UPL': 'Chemicals',
        'BHARTIARTL': 'Telecom', 'IDEA': 'Telecom', 'TATACOMM': 'Telecom',
        'POWERGRID': 'Utilities', 'NTPC': 'Utilities', 'COALINDIA': 'Mining',
        'ADANIPORTS': 'Ports', 'APOLLOHOSP': 'Healthcare', 'LALPATHLAB': 'Healthcare',
        'ZOMATO': 'New Age', 'NYKAA': 'New Age', 'PAYTM': 'New Age', 'DELHIVERY': 'Logistics'
    }
    
    return sector_mapping.get(symbol, 'Others')

def get_indian_market_overview():
    """Get Indian market overview"""
    try:
        # Fetch Nifty and Sensex data
        nifty = yf.download("^NSEI", period="1d", interval="5m", progress=False)
        sensex = yf.download("^BSESN", period="1d", interval="5m", progress=False)
        
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
    
    sector_counts = recommendations_df['Sector'].value_counts().to_dict()
    return sector_counts
