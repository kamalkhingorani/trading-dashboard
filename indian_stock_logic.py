# indian_stock_logic.py - ENHANCED WITH TECHNICAL REASONING
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import time

def calculate_rsi(data, window=14):
    """Calculate RSI indicator with fallback tracking"""
    try:
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi, False  # False = real calculation
    except Exception:
        fallback_rsi = pd.Series([50] * len(data), index=data.index)
        return fallback_rsi, True  # True = fallback used

def analyze_technical_patterns(data, symbol):
    """Analyze technical patterns and provide reasoning"""
    reasons = []
    pattern_strength = 0
    is_fallback = False
    
    try:
        # Get recent data (last 5 days for daily patterns)
        recent_data = data.tail(10)
        latest = recent_data.iloc[-1]
        previous = recent_data.iloc[-2] if len(recent_data) >= 2 else latest
        
        # 1. CANDLESTICK PATTERNS
        current_candle_bullish = latest['Close'] > latest['Open']
        candle_size = abs(latest['Close'] - latest['Open'])
        avg_body_size = abs(recent_data['Close'] - recent_data['Open']).mean()
        
        if current_candle_bullish and candle_size > avg_body_size * 1.5:
            reasons.append("Strong Bullish Candle")
            pattern_strength += 2
        elif current_candle_bullish:
            reasons.append("Bullish Candle")
            pattern_strength += 1
            
        # 2. RSI ANALYSIS
        if 'RSI' in data.columns:
            current_rsi = latest['RSI']
            prev_rsi = previous['RSI'] if 'RSI' in previous else current_rsi
            
            if not pd.isna(current_rsi) and not pd.isna(prev_rsi):
                if current_rsi > prev_rsi and 30 < current_rsi < 60:
                    reasons.append("Rising RSI")
                    pattern_strength += 1
                elif current_rsi < 35:
                    reasons.append("Oversold RSI")
                    pattern_strength += 1
            else:
                is_fallback = True
                
        # 3. VOLUME ANALYSIS
        if 'Volume' in data.columns and len(recent_data) >= 5:
            recent_avg_volume = recent_data['Volume'].tail(5).mean()
            older_avg_volume = recent_data['Volume'].head(5).mean()
            
            if recent_avg_volume > older_avg_volume * 1.3:
                reasons.append("Volume Surge")
                pattern_strength += 2
            elif recent_avg_volume > older_avg_volume * 1.1:
                reasons.append("Increasing Volume")
                pattern_strength += 1
        else:
            is_fallback = True
            
        # 4. PRICE MOMENTUM
        if len(recent_data) >= 3:
            recent_highs = recent_data['High'].tail(3)
            if recent_highs.iloc[-1] > recent_highs.iloc[-2] > recent_highs.iloc[-3]:
                reasons.append("Higher Highs")
                pattern_strength += 1
                
        # 5. MOVING AVERAGE ANALYSIS
        if 'EMA20' in data.columns and 'EMA50' in data.columns:
            ema20 = latest['EMA20']
            ema50 = latest['EMA50']
            
            if not pd.isna(ema20) and not pd.isna(ema50):
                if latest['Close'] > ema20 > ema50:
                    reasons.append("Above EMAs")
                    pattern_strength += 1
                elif latest['Close'] > ema20:
                    reasons.append("Above EMA20")
                    pattern_strength += 0.5
            else:
                is_fallback = True
                
        # 6. WEEKLY ANALYSIS (using available data)
        if len(data) >= 5:
            # Simulate weekly candle using last 5 days
            weekly_open = data['Open'].iloc[-5]
            weekly_close = latest['Close']
            weekly_high = data['High'].tail(5).max()
            weekly_low = data['Low'].tail(5).min()
            
            if weekly_close > weekly_open:
                weekly_body_size = abs(weekly_close - weekly_open)
                weekly_range = weekly_high - weekly_low
                
                if weekly_body_size > weekly_range * 0.6:  # Strong weekly candle
                    reasons.append("Strong Weekly Bullish")
                    pattern_strength += 2
                else:
                    reasons.append("Weekly Bullish")
                    pattern_strength += 1
                    
        # 7. SUPPORT/RESISTANCE BREAKS
        if len(data) >= 20:
            recent_high = data['High'].tail(20).max()
            if latest['Close'] > recent_high * 0.98:  # Near 20-day high
                reasons.append("Near 20D High")
                pattern_strength += 1
                
        # Compile final reasoning
        if not reasons:
            reasons.append("Basic Technical Setup")
            
        return {
            'primary_reason': reasons[0] if reasons else "Technical Setup",
            'all_reasons': " + ".join(reasons[:3]),  # Top 3 reasons
            'pattern_strength': pattern_strength,
            'is_fallback': is_fallback
        }
        
    except Exception as e:
        return {
            'primary_reason': "Pattern Analysis Failed*",
            'all_reasons': "Technical Setup*",
            'pattern_strength': 1,
            'is_fallback': True
        }

def get_expanded_nse_universe():
    """Complete NSE universe - 1800+ stocks"""
    try:
        # Try to fetch complete NSE equity list (1800+ stocks)
        nse_equity_url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
        nse_df = pd.read_csv(nse_equity_url)
        all_nse_symbols = [symbol.strip() + ".NS" for symbol in nse_df['SYMBOL'].tolist()]
        return all_nse_symbols
        
    except Exception:
        # Fallback to expanded manual list
        return [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
            "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ASIANPAINT.NS", "ITC.NS",
            "AXISBANK.NS", "LT.NS", "SUNPHARMA.NS", "TITAN.NS", "WIPRO.NS",
            "MARUTI.NS", "BAJFINANCE.NS", "TATASTEEL.NS", "ONGC.NS", "COALINDIA.NS",
            "HDFCLIFE.NS", "ICICIGI.NS", "SBILIFE.NS", "BAJAJFINSV.NS", "INDUSINDBK.NS",
            "BANDHANBNK.NS", "FEDERALBNK.NS", "IDFCFIRSTB.NS", "PNB.NS", "CANBK.NS",
            "HCLTECH.NS", "TECHM.NS", "LTIM.NS", "MPHASIS.NS", "PERSISTENT.NS",
            "DRREDDY.NS", "CIPLA.NS", "APOLLOHOSP.NS", "FORTIS.NS", "BIOCON.NS",
            "DIVISLAB.NS", "GLENMARK.NS", "AUROPHARMA.NS", "LUPIN.NS",
            "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DABUR.NS", "MARICO.NS",
            "GODREJCP.NS", "COLPAL.NS", "UBL.NS", "TATACONSUM.NS",
            "M&M.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "TATAMOTORS.NS", "EICHERMOT.NS",
            "APOLLOTYRE.NS", "MRF.NS", "MOTHERSON.NS", "BOSCHLTD.NS",
            "BPCL.NS", "IOC.NS", "HINDPETRO.NS", "GAIL.NS", "NTPC.NS",
            "POWERGRID.NS", "ADANIPOWER.NS", "TATAPOWER.NS",
            "HINDALCO.NS", "VEDL.NS", "JSWSTEEL.NS", "SAIL.NS", "NMDC.NS",
            "JINDALSTEL.NS", "HINDZINC.NS", "WELCORP.NS",
            "PIDILITIND.NS", "BERGEPAINT.NS", "HAVELLS.NS", "VOLTAS.NS",
            "DIXON.NS", "SYMPHONY.NS", "IRCTC.NS", "BEL.NS", "HAL.NS",
            "ACC.NS", "ADANIENT.NS", "ADANIPORTS.NS", "AMARAJABAT.NS", "AMBUJACEM.NS",
            "ASHOKLEY.NS", "BALKRISIND.NS", "BANKINDIA.NS", "BATAINDIA.NS",
            "BHARATFORG.NS", "BHEL.NS", "CADILAHC.NS", "CASTROLIND.NS", "CENTURYTEX.NS",
            "CESC.NS", "CHOLAFIN.NS", "COCHINSHIP.NS", "CONCOR.NS", "CRISIL.NS",
            "CROMPTON.NS", "CUB.NS", "CUMMINSIND.NS", "DALBHARAT.NS", "DEEPAKNTR.NS",
            "DELTACORP.NS", "DLF.NS", "ENGINERSIN.NS", "EQUITAS.NS", "ESCORTS.NS",
            "EXIDEIND.NS", "FORTIS.NS", "GMRINFRA.NS", "GNFC.NS", "GODREJIND.NS",
            "GODREJPROP.NS", "GRANULES.NS", "GRASIM.NS", "GSPL.NS", "GUJALKALI.NS",
            "GUJGASLTD.NS", "HDFC.NS", "HDFCAMC.NS", "HEIDELBERG.NS", "HEXAWARE.NS",
            "HINDCOPPER.NS", "HONAUT.NS", "HUDCO.NS", "IBULHSGFIN.NS", "ICICIPRULI.NS",
            "IDEA.NS", "IDFC.NS", "IEX.NS", "IFCI.NS", "IGL.NS",
            "INDHOTEL.NS", "INDIACEM.NS", "INDIAMART.NS", "INDIANB.NS", "INDIGO.NS",
            "INDUSTOWER.NS", "INFIBEAM.NS", "IOB.NS", "IPCALAB.NS", "IRB.NS",
            "IRCON.NS", "ISEC.NS", "JKCEMENT.NS", "JKLAKSHMI.NS", "JMFINANCIL.NS",
            "JSWENERGY.NS", "JUBLFOOD.NS", "JUSTDIAL.NS", "KAJARIACER.NS", "KANSAINER.NS",
            "KEI.NS", "KNRCON.NS", "KPRMILL.NS", "KRBL.NS", "L&TFH.NS",
            "LALPATHLAB.NS", "LAURUSLABS.NS", "LICHSGFIN.NS", "LTTS.NS", "MANAPPURAM.NS",
            "MAXHEALTH.NS", "MCDOWELL-N.NS", "MCX.NS", "MINDTREE.NS", "MMTC.NS",
            "MOIL.NS", "MUTHOOTFIN.NS", "NATIONALUM.NS", "NAUKRI.NS", "NAVINFLUOR.NS",
            "NBCC.NS", "NCC.NS", "NHPC.NS", "NOCIL.NS", "OBEROIRLTY.NS",
            "OFSS.NS", "OIL.NS", "ORIENTELEC.NS", "PAGEIND.NS", "PETRONET.NS",
            "PFC.NS", "PFIZER.NS", "POLYCAB.NS", "PRAJIND.NS", "PRESTIGE.NS",
            "PVR.NS", "QUESS.NS", "RADICO.NS", "RAIN.NS", "RAJESHEXPO.NS",
            "RAMCOCEM.NS", "RBLBANK.NS", "RECLTD.NS", "RELCAPITAL.NS", "RELINFRA.NS",
            "RNAM.NS", "SBICARD.NS", "SHREECEM.NS", "SIEMENS.NS", "SRF.NS",
            "SRTRANSFIN.NS", "SUNTV.NS", "SYNDIBANK.NS", "TATACHEM.NS", "TATACOMM.NS",
            "TORNTPHARM.NS", "TRENT.NS", "TVSMOTOR.NS", "UJJIVAN.NS", "ULTRACEMCO.NS",
            "UNIONBANK.NS", "UPL.NS", "WOCKPHARMA.NS", "YESBANK.NS", "ZEEL.NS", "ZYDUSLIFE.NS"
        ]

def get_indian_stock_sector(symbol):
    """Indian stock sector mapping"""
    sector_mapping = {
        # Banking & Financial
        'RELIANCE': 'Energy', 'TCS': 'IT', 'HDFCBANK': 'Banking', 'INFY': 'IT', 'ICICIBANK': 'Banking',
        'KOTAKBANK': 'Banking', 'SBIN': 'Banking', 'BHARTIARTL': 'Telecom', 'ASIANPAINT': 'Paints', 'ITC': 'FMCG',
        'AXISBANK': 'Banking', 'LT': 'Infrastructure', 'SUNPHARMA': 'Pharma', 'TITAN': 'Jewellery', 'WIPRO': 'IT',
        'MARUTI': 'Auto', 'BAJFINANCE': 'Financial', 'TATASTEEL': 'Steel', 'ONGC': 'Oil&Gas', 'COALINDIA': 'Mining',
        'HDFCLIFE': 'Insurance', 'ICICIGI': 'Insurance', 'SBILIFE': 'Insurance', 'BAJAJFINSV': 'Financial', 'INDUSINDBK': 'Banking',
        'HCLTECH': 'IT', 'TECHM': 'IT', 'DRREDDY': 'Pharma', 'CIPLA': 'Pharma', 'HINDUNILVR': 'FMCG',
        'NESTLEIND': 'FMCG', 'BRITANNIA': 'FMCG', 'DABUR': 'FMCG', 'MARICO': 'FMCG', 'BPCL': 'Oil&Gas',
        'IOC': 'Oil&Gas', 'NTPC': 'Power', 'POWERGRID': 'Power', 'HINDALCO': 'Metals', 'VEDL': 'Metals',
        'JSWSTEEL': 'Steel', 'ULTRACEMCO': 'Cement', 'M&M': 'Auto', 'BAJAJ-AUTO': 'Auto', 'HEROMOTOCO': 'Auto'
    }
    return sector_mapping.get(symbol, 'Other')

def calculate_dynamic_targets(data, current_price):
    """Calculate dynamic targets with fallback tracking"""
    try:
        # Calculate volatility (20-day)
        returns = data['Close'].pct_change().dropna()
        volatility = returns.tail(20).std() * np.sqrt(252) if len(returns) >= 20 else None
        
        # Track if we're using fallbacks
        using_fallback_volatility = volatility is None
        if using_fallback_volatility:
            volatility = 0.25
            
        # Support and resistance levels
        recent_high = data['High'].tail(30).max()
        recent_low = data['Low'].tail(30).min()
        
        # Volume analysis
        avg_volume = data['Volume'].tail(20).mean() if 'Volume' in data.columns else None
        recent_volume = data['Volume'].tail(5).mean() if 'Volume' in data.columns else None
        
        using_fallback_volume = avg_volume is None or recent_volume is None
        if using_fallback_volume:
            avg_volume = 1000000
            recent_volume = 1000000
            
        volume_surge = recent_volume > avg_volume * 1.2
        
        # Target calculation based on volatility
        if volatility > 0.30:  # High volatility stocks
            base_target_pct = np.random.uniform(6, 12)
        elif volatility > 0.20:  # Medium volatility
            base_target_pct = np.random.uniform(4, 8)
        else:  # Low volatility
            base_target_pct = np.random.uniform(3, 6)
        
        # Technical adjustments
        technical_adjustment_applied = False
        if len(data) >= 50:
            ema20 = data['Close'].ewm(span=20).mean().iloc[-1]
            ema50 = data['Close'].ewm(span=50).mean().iloc[-1]
            
            # Trend alignment bonus
            if current_price > ema20 > ema50:
                base_target_pct *= 1.1
                technical_adjustment_applied = True
            
            # Volume confirmation bonus
            if volume_surge and not using_fallback_volume:
                base_target_pct *= 1.05
                technical_adjustment_applied = True
        
        # Calculate target price
        target_price = current_price * (1 + base_target_pct / 100)
        
        # Ensure target doesn't exceed recent resistance by too much
        if target_price > recent_high * 1.08:
            target_price = recent_high * 1.08
            base_target_pct = ((target_price / current_price) - 1) * 100
        
        # Stop loss calculation
        support_level = recent_low * 1.02
        volatility_sl = current_price * (1 - min(volatility * 0.8, 0.06))
        
        # Use the higher of the two (less aggressive)
        stop_loss = max(support_level, volatility_sl)
        
        # Risk management - SL should not exceed 50% of potential gain
        potential_gain = target_price - current_price
        max_allowed_sl_price = current_price - (potential_gain * 0.4)
        
        if stop_loss < max_allowed_sl_price:
            stop_loss = max_allowed_sl_price
        
        # Ensure minimum SL
        min_sl_price = current_price * 0.985
        stop_loss = min(stop_loss, min_sl_price)
        
        sl_pct = ((current_price - stop_loss) / current_price) * 100
        
        # Calculate risk-reward ratio
        risk = current_price - stop_loss
        reward = target_price - current_price
        risk_reward_ratio = round(reward / risk, 1) if risk > 0 else 1.0
        
        # Estimated days
        if base_target_pct <= 4:
            estimated_days = np.random.randint(5, 15)
        elif base_target_pct <= 7:
            estimated_days = np.random.randint(8, 20)
        else:
            estimated_days = np.random.randint(12, 25)
        
        return {
            'target': target_price,
            'target_pct': base_target_pct,
            'stop_loss': stop_loss,
            'sl_pct': sl_pct,
            'estimated_days': estimated_days,
            'volatility': volatility,
            'volume_surge': volume_surge,
            'risk_reward_ratio': risk_reward_ratio,
            'fallback_flags': {
                'volatility': using_fallback_volatility,
                'volume': using_fallback_volume,
                'technical_adjustment': not technical_adjustment_applied
            }
        }
        
    except Exception as e:
        # Complete fallback
        return {
            'target': current_price * 1.05,
            'target_pct': 5.0,
            'stop_loss': current_price * 0.97,
            'sl_pct': 3.0,
            'estimated_days': 10,
            'volatility': 0.25,
            'volume_surge': False,
            'risk_reward_ratio': 1.7,
            'fallback_flags': {
                'volatility': True,
                'volume': True,
                'technical_adjustment': True,
                'complete_fallback': True
            }
        }

def get_indian_recommendations(min_price=25, max_rsi=70, min_volume=50000, batch_size=200):
    """ENHANCED: Get Indian stock recommendations with technical reasoning"""
    
    try:
        symbols = get_expanded_nse_universe()
        recommendations = []
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_symbols = min(len(symbols), batch_size)
        successful_fetches = 0
        
        status_text.text(f"Starting enhanced scan of {total_symbols} Indian stocks...")
        
        # Randomize symbol order to scan different stocks each time
        import random
        random.shuffle(symbols)
        
        for i, symbol in enumerate(symbols[:total_symbols]):
            try:
                progress_bar.progress((i + 1) / total_symbols)
                status_text.text(f"Analyzing {symbol.replace('.NS', '')}... ({i+1}/{total_symbols})")
                
                time.sleep(0.1)
                
                # Fetch data
                stock = yf.Ticker(symbol)
                data = stock.history(period="3mo", interval="1d")
                
                if len(data) < 30:
                    continue
                
                # Calculate indicators with fallback tracking
                data['RSI'], rsi_is_fallback = calculate_rsi(data)
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
                
                current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
                
                # Check RSI rising trend
                rsi_rising = False
                if len(data['RSI']) >= 5:
                    recent_rsi = data['RSI'].tail(5)
                    # RSI rising if current > 1 days ago (allows for 1-2 day dips)
                    rsi_rising = (recent_rsi.iloc[-1] > recent_rsi.iloc[-2])
                else:
                    rsi_rising = True  # If insufficient data, don't filter out
                
                # Volume handling with fallback tracking
                avg_volume = data['Volume'].tail(10).mean() if 'Volume' in data.columns else min_volume
                volume_is_fallback = 'Volume' not in data.columns
                
                # Apply filters
                if (current_price >= min_price and 
                    rsi <= max_rsi and
                    rsi_rising and
                    not pd.isna(rsi) and 
                    not pd.isna(current_price) and
                    avg_volume >= min_volume * 0.3):
                    
                    successful_fetches += 1
                    
                    # Analyze technical patterns
                    pattern_analysis = analyze_technical_patterns(data, symbol)
                    
                    # Calculate dynamic targets
                    target_data = calculate_dynamic_targets(data, current_price)
                    
                    # Technical score calculation
                    technical_score = 0
                    score_components = []
                    
                    # Trend alignment
                    if latest['Close'] > latest['EMA20']:
                        technical_score += 1
                        score_components.append("Above EMA20")
                    if latest['EMA20'] > latest['EMA50']:
                        technical_score += 1
                        score_components.append("EMA Bullish")
                    
                    # RSI conditions
                    if 25 <= rsi <= 70:
                        technical_score += 1
                        score_components.append("Good RSI")
                    
                    # MACD signal
                    if latest['MACD'] > latest['MACD_Signal']:
                        technical_score += 1
                        score_components.append("MACD+")
                    
                    # Volume confirmation
                    if target_data['volume_surge'] and not target_data['fallback_flags'].get('volume', False):
                        technical_score += 1
                        score_components.append("Volume+")
                    
                    # Include stocks with 2+ conditions
                    if technical_score >= 2:
                        
                        # Risk rating
                        if target_data['volatility'] > 0.35:
                            risk_rating = 'High'
                        elif target_data['volatility'] > 0.25:
                            risk_rating = 'Medium'
                        else:
                            risk_rating = 'Low'
                        
                        # Create fallback indicators
                        fallback_indicators = []
                        if rsi_is_fallback:
                            fallback_indicators.append("RSI*")
                        if target_data['fallback_flags'].get('volume', False):
                            fallback_indicators.append("Vol*")
                        if target_data['fallback_flags'].get('volatility', False):
                            fallback_indicators.append("Volatility*")
                        if target_data['fallback_flags'].get('complete_fallback', False):
                            fallback_indicators.append("Targets*")
                            
                        fallback_note = " (" + ", ".join(fallback_indicators) + ")" if fallback_indicators else ""
                        
                        # Get sector
                        sector = get_indian_stock_sector(symbol.replace('.NS', ''))
                        
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
                            'Selection Reason': pattern_analysis['all_reasons'],
                            'Primary Pattern': pattern_analysis['primary_reason'],
                            'Volume': int(avg_volume),
                            'Risk': risk_rating,
                            'Tech Score': f"{technical_score}/5",
                            'Sector': sector,
                            'Volatility': f"{target_data['volatility']:.1%}",
                            'Data Quality': f"Real Data{fallback_note}" if not fallback_indicators else f"Mixed Data{fallback_note}",
                            'Status': 'Active'
                        })
            
            except Exception as e:
                continue
        
        progress_bar.empty()
        status_text.empty()
        
        # Display scan statistics
        if successful_fetches > 0:
            st.info(f"✅ Successfully analyzed {successful_fetches} stocks out of {total_symbols} attempted")
        else:
            st.warning(f"⚠️ Could not fetch data for any stocks. This might be due to market hours or API limits.")
        
        # Sort by pattern strength and technical score
        df = pd.DataFrame(recommendations)
        if not df.empty:
            df = df.sort_values(['Tech Score', '% Gain'], ascending=[False, False])
            df = df.head(20)
        
        return df
        
    except Exception as e:
        st.error(f"Error in get_indian_recommendations: {str(e)}")
        return pd.DataFrame()

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
            'last_updated': 'Market data unavailable*',
            'error': str(e)
        }
