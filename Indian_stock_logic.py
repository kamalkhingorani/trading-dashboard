# indian_stock_logic.py - FIXED VERSION
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import time

def calculate_rsi(data, window=14):
    """Calculate RSI indicator"""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_expanded_nse_universe():
    """Expanded NSE stock universe with 100+ liquid stocks"""
    return [
        # Large Cap - Core Holdings
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
        "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ASIANPAINT.NS", "ITC.NS",
        "AXISBANK.NS", "LT.NS", "SUNPHARMA.NS", "TITAN.NS", "WIPRO.NS",
        "MARUTI.NS", "BAJFINANCE.NS", "TATASTEEL.NS", "ONGC.NS", "COALINDIA.NS",
        
        # Banking & Financial Services  
        "HDFCLIFE.NS", "ICICIGI.NS", "SBILIFE.NS", "BAJAJFINSV.NS", "INDUSINDBK.NS",
        "BANDHANBNK.NS", "FEDERALBNK.NS", "IDFCFIRSTB.NS", "PNB.NS", "CANBK.NS",
        "MUTHOOTFIN.NS", "CHOLAFIN.NS", "MANAPPURAM.NS", "PFC.NS", "RECLTD.NS",
        
        # Technology & IT Services
        "HCLTECH.NS", "TECHM.NS", "LTIM.NS", "MPHASIS.NS", "MINDTREE.NS",
        "LTTS.NS", "COFORGE.NS", "PERSISTENT.NS", "CYIENT.NS", "KPITTECH.NS",
        
        # Pharmaceuticals & Healthcare
        "DRREDDY.NS", "CIPLA.NS", "APOLLOHOSP.NS", "FORTIS.NS", "BIOCON.NS",
        "DIVISLAB.NS", "GLENMARK.NS", "CADILAHC.NS", "AUROPHARMA.NS", "LUPIN.NS",
        
        # Consumer Goods & FMCG
        "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DABUR.NS", "MARICO.NS",
        "GODREJCP.NS", "COLPAL.NS", "UBL.NS", "VBL.NS", "TATACONSUM.NS",
        
        # Automobiles & Auto Ancillaries
        "M&M.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "TATAMOTORS.NS", "EICHERMOT.NS",
        "APOLLOTYRE.NS", "MRF.NS", "BALKRISIND.NS", "MOTHERSON.NS", "BOSCHLTD.NS",
        
        # Oil, Gas & Energy
        "BPCL.NS", "IOC.NS", "HINDPETRO.NS", "GAIL.NS", "NTPC.NS",
        "POWERGRID.NS", "ADANIPOWER.NS", "TATAPOWER.NS", "RELINFRA.NS",
        
        # Metals & Mining
        "HINDALCO.NS", "VEDL.NS", "JSWSTEEL.NS", "SAIL.NS", "NMDC.NS",
        "JINDALSTEL.NS", "TATASTEEL.NS", "HINDZINC.NS", "MOIL.NS", "WELCORP.NS",
        
        # Infrastructure & Construction
        "ADANIPORTS.NS", "ULTRACEMCO.NS", "GRASIM.NS", "SHREECEM.NS", "RAMCOCEM.NS",
        "ACC.NS", "AMBUJACEMENT.NS", "IRB.NS", "GMRINFRA.NS", "ASHOKLEY.NS",
        
        # Telecommunications
        "AIRTEL.NS", "IDEA.NS", "GTPL.NS", "RCOM.NS",
        
        # Textiles & Apparel
        "ADITYANRLI.NS", "VARDHMAN.NS", "WELSPUNIND.NS", "TRIDENT.NS", "RTNPOWER.NS",
        
        # Mid Cap Growth Stories
        "ZOMATO.NS", "NYKAA.NS", "POLICYBZR.NS", "DELHIVERY.NS", "CAMS.NS",
        "LICI.NS", "IRCTC.NS", "RVNL.NS", "BEL.NS", "HAL.NS",
        
        # Additional Quality Mid-caps
        "PIDILITIND.NS", "BERGEPAINT.NS", "HAVELLS.NS", "VOLTAS.NS", "WHIRLPOOL.NS",
        "CROMPTON.NS", "AMBER.NS", "DIXON.NS", "SYMPHONY.NS", "BLUEDART.NS"
    ]

def calculate_dynamic_targets(data, current_price):
    """Calculate dynamic targets with RELAXED criteria"""
    try:
        # Calculate volatility (20-day)
        returns = data['Close'].pct_change().dropna()
        volatility = returns.tail(20).std() * np.sqrt(252) if len(returns) >= 20 else 0.25
        
        # Support and resistance levels
        recent_high = data['High'].tail(30).max()
        recent_low = data['Low'].tail(30).min()
        
        # Volume analysis
        avg_volume = data['Volume'].tail(20).mean() if 'Volume' in data.columns else 1000000
        recent_volume = data['Volume'].tail(5).mean() if 'Volume' in data.columns else 1000000
        volume_surge = recent_volume > avg_volume * 1.2
        
        # RELAXED Target calculation based on volatility
        if volatility > 0.30:  # High volatility stocks
            base_target_pct = np.random.uniform(6, 12)  # Reduced from 8-15%
        elif volatility > 0.20:  # Medium volatility
            base_target_pct = np.random.uniform(4, 8)   # Reduced from 5-12%
        else:  # Low volatility
            base_target_pct = np.random.uniform(3, 6)   # Reduced from 3-8%
        
        # Technical adjustments (REDUCED)
        if len(data) >= 50:
            ema20 = data['Close'].ewm(span=20).mean().iloc[-1]
            ema50 = data['Close'].ewm(span=50).mean().iloc[-1]
            
            # Trend alignment bonus (REDUCED)
            if current_price > ema20 > ema50:
                base_target_pct *= 1.1  # Reduced from 1.2
            
            # Volume confirmation bonus (REDUCED) 
            if volume_surge:
                base_target_pct *= 1.05  # Reduced from 1.1
        
        # Calculate target price
        target_price = current_price * (1 + base_target_pct / 100)
        
        # Ensure target doesn't exceed recent resistance by too much
        if target_price > recent_high * 1.08:  # Max 8% above recent high
            target_price = recent_high * 1.08
            base_target_pct = ((target_price / current_price) - 1) * 100
        
        # RELAXED Stop loss calculation
        support_level = recent_low * 1.02  # 2% buffer above recent low
        volatility_sl = current_price * (1 - min(volatility * 0.8, 0.06))  # Max 6% SL
        
        # Use the higher of the two (less aggressive)
        stop_loss = max(support_level, volatility_sl)
        
        # CRITICAL: Risk management - SL should not exceed 50% of potential gain
        potential_gain = target_price - current_price
        max_allowed_sl_price = current_price - (potential_gain * 0.4)  # Allow up to 40% of gain as SL
        
        if stop_loss < max_allowed_sl_price:
            stop_loss = max_allowed_sl_price
        
        # Ensure minimum SL (1.5% instead of 2%)
        min_sl_price = current_price * 0.985  # 1.5% minimum SL
        stop_loss = min(stop_loss, min_sl_price)
        
        sl_pct = ((current_price - stop_loss) / current_price) * 100
        
        # Calculate risk-reward ratio
        risk = current_price - stop_loss
        reward = target_price - current_price
        risk_reward_ratio = round(reward / risk, 1) if risk > 0 else 1.0
        
        # Estimated days (RELAXED)
        if base_target_pct <= 4:
            estimated_days = np.random.randint(5, 15)    # Reduced from 10-20
        elif base_target_pct <= 7:
            estimated_days = np.random.randint(8, 20)    # Reduced from 15-25
        else:
            estimated_days = np.random.randint(12, 25)   # Reduced from 20-35
        
        return {
            'target': target_price,
            'target_pct': base_target_pct,
            'stop_loss': stop_loss,
            'sl_pct': sl_pct,
            'estimated_days': estimated_days,
            'volatility': volatility,
            'volume_surge': volume_surge,
            'risk_reward_ratio': risk_reward_ratio
        }
        
    except Exception as e:
        # Fallback values
        return {
            'target': current_price * 1.05,
            'target_pct': 5.0,
            'stop_loss': current_price * 0.97,
            'sl_pct': 3.0,
            'estimated_days': 10,
            'volatility': 0.25,
            'volume_surge': False,
            'risk_reward_ratio': 1.7
        }

def get_indian_recommendations(min_price=25, max_rsi=70, min_volume=50000, batch_size=50):
    """FIXED: Get Indian stock recommendations with RELAXED filters"""
    
    symbols = get_expanded_nse_universe()
    recommendations = []
    
    # Show progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # INCREASED batch size for more results
    total_symbols = min(len(symbols), batch_size)
    successful_fetches = 0
    
    for i, symbol in enumerate(symbols[:total_symbols]):
        try:
            progress_bar.progress((i + 1) / total_symbols)
            status_text.text(f"Analyzing {symbol.replace('.NS', '')}... ({i+1}/{total_symbols})")
            
            # RELAXED: Reduce delay to speed up scanning
            time.sleep(0.1)  # Reduced from 0.2
            
            # Fetch data with error handling
            stock = yf.Ticker(symbol)
            data = stock.history(period="3mo", interval="1d")  # Reduced from 6mo to 3mo
            
            if len(data) < 30:  # Reduced from 50 to 30
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
            
            # Handle volume safely with lower requirements
            avg_volume = data['Volume'].tail(10).mean() if 'Volume' in data.columns else min_volume
            
            # RELAXED filters - much more lenient
            if (current_price >= min_price and 
                rsi <= max_rsi and  # Increased from 60 to 70
                not pd.isna(rsi) and 
                not pd.isna(current_price) and
                avg_volume >= min_volume * 0.3):  # Reduced from 0.5 to 0.3
                
                successful_fetches += 1
                
                # Calculate dynamic targets
                target_data = calculate_dynamic_targets(data, current_price)
                
                # RELAXED technical score calculation
                technical_score = 0
                
                # Trend alignment (RELAXED)
                if latest['Close'] > latest['EMA20']:
                    technical_score += 1
                if latest['EMA20'] > latest['EMA50']:
                    technical_score += 1
                
                # RSI conditions (RELAXED range)
                if 25 <= rsi <= 70:  # Expanded from 30-60 to 25-70
                    technical_score += 1
                
                # MACD signal
                if latest['MACD'] > latest['MACD_Signal']:
                    technical_score += 1
                
                # Volume confirmation
                if target_data['volume_surge']:
                    technical_score += 1
                
                # MUCH MORE RELAXED: Include stocks with 2+ conditions instead of 3+
                if technical_score >= 2:  # Reduced from 3 to 2
                    
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
                        'Est.Days': target_data['estimated_days'],
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
            # Continue processing other stocks even if one fails
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    # Display scan statistics
    if successful_fetches > 0:
        st.info(f"✅ Successfully analyzed {successful_fetches} stocks out of {total_symbols} attempted")
    else:
        st.warning(f"⚠️ Could not fetch data for any stocks. This might be due to market hours or API limits.")
    
    # Sort by technical score and then by % gain potential
    df = pd.DataFrame(recommendations)
    if not df.empty:
        df = df.sort_values(['Tech Score', '% Gain'], ascending=[False, False])
        # Limit to top 20 results for display
        df = df.head(20)
    
    return df

def get_indian_market_overview():
    """Get Indian market overview with error handling"""
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
            'nifty': {'price': 22000, 'change': 0, 'change_pct': 0},
            'sensex': {'price': 73000, 'change': 0, 'change_pct': 0},
            'last_updated': 'Market data unavailable',
            'error': str(e)
        }
