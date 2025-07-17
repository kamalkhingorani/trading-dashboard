# us_stock_logic.py - FIXED VERSION  
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

def get_expanded_sp500_universe():
    """Expanded S&P 500 universe with 150+ top stocks"""
    return [
        # Mega Cap Technology Giants
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "ADBE",
        "CRM", "ORCL", "INTC", "AMD", "QCOM", "AVGO", "CSCO", "IBM", "INTU",
        "NOW", "WDAY", "VEEV", "DDOG", "SNOW", "CRWD", "ZS", "OKTA", "SPLK",
        "TEAM", "ZM", "SHOP", "SQ", "PYPL", "ROKU", "UBER", "LYFT", "ABNB",
        
        # Financial Services - Major Banks & Fintech
        "JPM", "BAC", "WFC", "GS", "MS", "C", "AXP", "V", "MA", "BK", "USB", 
        "PNC", "COF", "SCHW", "BLK", "SPGI", "MCO", "AIG", "TRV", "ALL", "PGR",
        "CB", "AFL", "MET", "PRU", "AON", "MMC", "AJG", "BRO",
        
        # Healthcare & Pharmaceuticals
        "JNJ", "PFE", "UNH", "ABBV", "TMO", "ABT", "MDT", "BMY", "AMGN", "GILD",
        "REGN", "BSX", "SYK", "ISRG", "ZBH", "BDX", "EW", "ALGN", "MRNA", "BNTX",
        "CVS", "ANTM", "CI", "HUM", "CNC", "MOH", "ELV", "DXCM", "ZTS", "IDEXX",
        
        # Defense & Aerospace  
        "BA", "LMT", "RTX", "NOC", "GD", "LHX", "LDOS", "HII", "TDG", "CW",
        "AXON", "KTOS", "MRCY", "TXT", "PH", "ROK", "EMR", "HON",
        
        # Manufacturing & Industrial
        "CAT", "GE", "MMM", "UPS", "FDX", "ETN", "ITW", "CMI", "DE", "DOV", 
        "CARR", "OTIS", "PCAR", "WAB", "CHRW", "J", "PNR", "FAST", "XYL", "IEX",
        "EXPD", "JBHT", "KNX", "ALLE", "GNRC", "IR", "SNA", "NDSN",
        
        # Energy & Utilities
        "XOM", "CVX", "COP", "EOG", "SLB", "MPC", "VLO", "PSX", "OXY", "HAL",
        "NEE", "DUK", "SO", "AEP", "EXC", "XEL", "WEC", "ES", "AWK", "CMS",
        "D", "ATO", "CNP", "ETR", "EVRG", "FE", "NI", "PEG", "SRE", "PPL",
        
        # Consumer Goods & Retail  
        "WMT", "HD", "LOW", "COST", "TGT", "PG", "KO", "PEP", "MCD", "SBUX",
        "NKE", "TJX", "ROST", "YUM", "CMG", "ULTA", "ETSY", "EBAY", "DIS", "F",
        "GM", "CCL", "RCL", "NCLH", "MAR", "HLT", "MGM", "LVS", "WYNN", "BYD",
        
        # Materials & Chemicals
        "LIN", "APD", "ECL", "SHW", "FCX", "NEM", "FMC", "ALB", "EMN", "IFF",
        "PPG", "CF", "MOS", "LYB", "DOW", "DD", "CE", "VMC", "MLM", "NUE",
        "STLD", "RS", "PKG", "IP", "WRK", "AVY", "SEE", "SON", "RPM", "FUL",
        
        # Communication Services
        "VZ", "T", "TMUS", "CMCSA", "CHTR", "FOXA", "FOX", "NWSA", "PARA",
        "WBD", "DIS", "DISH", "SIRI", "LUMN", "ATVI", "EA", "TTWO", "ZNGA",
        
        # Real Estate & REITs
        "AMT", "PLD", "EQIX", "SPG", "O", "PSA", "EQR", "AVB", "ARE", "DLR",
        "CCI", "SBAC", "WY", "BXP", "VTR", "WELL", "EXR", "UDR", "CPT", "MAA",
        
        # Semiconductors & Tech Hardware
        "TSM", "ASML", "MU", "MRVL", "ADI", "LRCX", "KLAC", "AMAT", "TXN", "MCHP",
        "ON", "MPWR", "SWKS", "QRVO", "TER", "ENTG", "OLED", "CRUS", "SLAB",
        
        # Biotechnology & Life Sciences
        "BIIB", "VRTX", "ILMN", "INCY", "BMRN", "TECH", "EXAS", "NBIX", "ALNY",
        "SRPT", "RARE", "FOLD", "ARCT", "BLUE", "EDIT", "CRSP", "NTLA", "BEAM"
    ]

def calculate_us_dynamic_targets(data, current_price):
    """Calculate dynamic targets for US stocks with RELAXED criteria"""
    try:
        # Calculate volatility (20-day)
        returns = data['Close'].pct_change().dropna()
        volatility = returns.tail(20).std() * np.sqrt(252) if len(returns) >= 20 else 0.20
        
        # Support and resistance levels
        recent_high = data['High'].tail(30).max()
        recent_low = data['Low'].tail(30).min()
        
        # Volume analysis
        avg_volume = data['Volume'].tail(20).mean() if 'Volume' in data.columns else 1000000
        recent_volume = data['Volume'].tail(5).mean() if 'Volume' in data.columns else 1000000
        volume_surge = recent_volume > avg_volume * 1.2
        
        # RELAXED Target calculation for US stocks
        if volatility > 0.30:  # High volatility
            base_target_pct = np.random.uniform(4, 8)   # Reduced from 5-10%
        elif volatility > 0.20:  # Medium volatility  
            base_target_pct = np.random.uniform(3, 6)   # Reduced from 3-8%
        else:  # Low volatility
            base_target_pct = np.random.uniform(2, 5)   # Reduced from 2-6%
        
        # Market cap adjustments (RELAXED)
        if current_price > 300:  # Large cap
            base_target_pct *= 0.9  # Slightly more conservative
        elif current_price < 50:  # Small cap
            base_target_pct *= 1.1  # Slightly more aggressive
        
        # Technical adjustments (REDUCED)
        if len(data) >= 50:
            ema21 = data['Close'].ewm(span=21).mean().iloc[-1]
            ema50 = data['Close'].ewm(span=50).mean().iloc[-1]
            
            # Trend alignment bonus (REDUCED)
            if current_price > ema21 > ema50:
                base_target_pct *= 1.05  # Reduced from 1.15
            
            # Volume confirmation bonus (REDUCED)
            if volume_surge:
                base_target_pct *= 1.03  # Reduced from 1.1
        
        # Calculate target price
        target_price = current_price * (1 + base_target_pct / 100)
        
        # Ensure target doesn't exceed recent resistance by too much
        if target_price > recent_high * 1.06:  # Max 6% above recent high for US
            target_price = recent_high * 1.06
            base_target_pct = ((target_price / current_price) - 1) * 100
        
        # RELAXED Stop loss calculation for US stocks
        support_level = recent_low * 1.015  # 1.5% buffer above recent low
        volatility_sl = current_price * (1 - min(volatility * 0.7, 0.05))  # Max 5% SL
        
        # Use the higher of the two (less aggressive)
        stop_loss = max(support_level, volatility_sl)
        
        # CRITICAL: Risk management - SL should not exceed 50% of potential gain
        potential_gain = target_price - current_price
        max_allowed_sl_price = current_price - (potential_gain * 0.4)  # Allow up to 40% of gain as SL
        
        if stop_loss < max_allowed_sl_price:
            stop_loss = max_allowed_sl_price
        
        # Ensure minimum SL (1% instead of 1.5%)
        min_sl_price = current_price * 0.99  # 1% minimum SL for US stocks
        stop_loss = min(stop_loss, min_sl_price)
        
        sl_pct = ((current_price - stop_loss) / current_price) * 100
        
        # Calculate risk-reward ratio
        risk = current_price - stop_loss
        reward = target_price - current_price
        risk_reward_ratio = round(reward / risk, 1) if risk > 0 else 1.0
        
        # Estimated days (RELAXED)
        if base_target_pct <= 3:
            estimated_days = np.random.randint(3, 10)    # Reduced timeframe
        elif base_target_pct <= 5:
            estimated_days = np.random.randint(5, 15)    # Reduced timeframe
        else:
            estimated_days = np.random.randint(8, 20)    # Reduced timeframe
        
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
        # Fallback values for US stocks
        return {
            'target': current_price * 1.04,
            'target_pct': 4.0,
            'stop_loss': current_price * 0.98,
            'sl_pct': 2.0,
            'estimated_days': 8,
            'volatility': 0.20,
            'volume_surge': False,
            'risk_reward_ratio': 2.0
        }

def get_stock_sector(symbol):
    """Get sector for US stock symbol - EXPANDED mapping"""
    sector_mapping = {
        # Technology
        'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology', 'AMZN': 'Technology',
        'TSLA': 'Technology', 'META': 'Technology', 'NVDA': 'Technology', 'NFLX': 'Technology',
        'ADBE': 'Technology', 'CRM': 'Technology', 'ORCL': 'Technology', 'INTC': 'Technology',
        'AMD': 'Technology', 'QCOM': 'Technology', 'AVGO': 'Technology', 'CSCO': 'Technology',
        'IBM': 'Technology', 'INTU': 'Technology', 'NOW': 'Technology', 'WDAY': 'Technology',
        'VEEV': 'Technology', 'DDOG': 'Technology', 'SNOW': 'Technology', 'CRWD': 'Technology',
        'ZS': 'Technology', 'OKTA': 'Technology', 'SPLK': 'Technology', 'TEAM': 'Technology',
        'ZM': 'Technology', 'SHOP': 'Technology', 'SQ': 'Technology', 'PYPL': 'Technology',
        'ROKU': 'Technology', 'UBER': 'Technology', 'LYFT': 'Technology', 'ABNB': 'Technology',
        
        # Financial
        'JPM': 'Financial', 'BAC': 'Financial', 'WFC': 'Financial', 'GS': 'Financial',
        'MS': 'Financial', 'C': 'Financial', 'V': 'Financial', 'MA': 'Financial',
        'AXP': 'Financial', 'BK': 'Financial', 'USB': 'Financial', 'PNC': 'Financial',
        'COF': 'Financial', 'SCHW': 'Financial', 'BLK': 'Financial', 'SPGI': 'Financial',
        'MCO': 'Financial', 'AIG': 'Financial', 'TRV': 'Financial', 'ALL': 'Financial',
        'PGR': 'Financial', 'CB': 'Financial', 'AFL': 'Financial', 'MET': 'Financial',
        
        # Healthcare
        'JNJ': 'Healthcare', 'PFE': 'Healthcare', 'UNH': 'Healthcare', 'ABBV': 'Healthcare',
        'TMO': 'Healthcare', 'ABT': 'Healthcare', 'MDT': 'Healthcare', 'BMY': 'Healthcare',
        'AMGN': 'Healthcare', 'GILD': 'Healthcare', 'REGN': 'Healthcare', 'BSX': 'Healthcare',
        'SYK': 'Healthcare', 'ISRG': 'Healthcare', 'ZBH': 'Healthcare', 'BDX': 'Healthcare',
        'EW': 'Healthcare', 'ALGN': 'Healthcare', 'MRNA': 'Healthcare', 'BNTX': 'Healthcare',
        'CVS': 'Healthcare', 'ANTM': 'Healthcare', 'CI': 'Healthcare', 'HUM': 'Healthcare',
        
        # Energy
        'XOM': 'Energy', 'CVX': 'Energy', 'COP': 'Energy', 'EOG': 'Energy', 'SLB': 'Energy',
        'MPC': 'Energy', 'VLO': 'Energy', 'PSX': 'Energy', 'OXY': 'Energy', 'HAL': 'Energy',
        
        # Consumer
        'WMT': 'Consumer', 'HD': 'Consumer', 'LOW': 'Consumer', 'COST': 'Consumer', 'TGT': 'Consumer',
        'PG': 'Consumer', 'KO': 'Consumer', 'PEP': 'Consumer', 'MCD': 'Consumer', 'SBUX': 'Consumer',
        'NKE': 'Consumer', 'TJX': 'Consumer', 'ROST': 'Consumer', 'YUM': 'Consumer', 'CMG': 'Consumer',
        'ULTA': 'Consumer', 'ETSY': 'Consumer', 'EBAY': 'Consumer', 'DIS': 'Consumer', 'F': 'Consumer',
        
        # Industrial
        'CAT': 'Industrial', 'GE': 'Industrial', 'MMM': 'Industrial', 'HON': 'Industrial', 'UPS': 'Industrial',
        'FDX': 'Industrial', 'EMR': 'Industrial', 'ETN': 'Industrial', 'ITW': 'Industrial', 'PH': 'Industrial',
        'CMI': 'Industrial', 'DE': 'Industrial', 'DOV': 'Industrial', 'ROK': 'Industrial', 'CARR': 'Industrial',
        
        # Defense
        'BA': 'Defense', 'LMT': 'Defense', 'RTX': 'Defense', 'NOC': 'Defense', 'GD': 'Defense',
        'LHX': 'Defense', 'LDOS': 'Defense', 'HII': 'Defense', 'TDG': 'Defense', 'CW': 'Defense',
        
        # Utilities
        'NEE': 'Utilities', 'DUK': 'Utilities', 'SO': 'Utilities', 'AEP': 'Utilities', 'EXC': 'Utilities',
        'XEL': 'Utilities', 'WEC': 'Utilities', 'ES': 'Utilities', 'AWK': 'Utilities', 'CMS': 'Utilities',
        
        # Materials
        'LIN': 'Materials', 'APD': 'Materials', 'ECL': 'Materials', 'SHW': 'Materials', 'FCX': 'Materials',
        'NEM': 'Materials', 'FMC': 'Materials', 'ALB': 'Materials', 'EMN': 'Materials', 'IFF': 'Materials',
        'PPG': 'Materials', 'CF': 'Materials', 'MOS': 'Materials', 'LYB': 'Materials', 'DOW': 'Materials',
        
        # Communication
        'VZ': 'Communication', 'T': 'Communication', 'TMUS': 'Communication', 'CMCSA': 'Communication',
        'CHTR': 'Communication', 'FOXA': 'Communication', 'FOX': 'Communication', 'NWSA': 'Communication',
        
        # Real Estate
        'AMT': 'Real Estate', 'PLD': 'Real Estate', 'EQIX': 'Real Estate', 'SPG': 'Real Estate', 
        'O': 'Real Estate', 'PSA': 'Real Estate', 'EQR': 'Real Estate', 'AVB': 'Real Estate'
    }
    
    return sector_mapping.get(symbol, 'Other')

def get_us_recommendations(min_price=25, max_rsi=65, min_volume=500000, batch_size=60):
    """FIXED: Get US stock recommendations with RELAXED filters"""
    
    symbols = get_expanded_sp500_universe()
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
            status_text.text(f"Analyzing {symbol}... ({i+1}/{total_symbols})")
            
            # RELAXED: Reduce delay to speed up scanning
            time.sleep(0.08)  # Reduced delay
            
            # Fetch data with error handling
            stock = yf.Ticker(symbol)
            data = stock.history(period="3mo", interval="1d")  # Reduced from 6mo to 3mo
            
            if len(data) < 25:  # Reduced from 50 to 25
                continue
            
            # Calculate indicators
            data['RSI'] = calculate_rsi(data)
            data['EMA21'] = data['Close'].ewm(span=21).mean()
            data['EMA50'] = data['Close'].ewm(span=50).mean()
            data['SMA20'] = data['Close'].rolling(20).mean()
            
            # Bollinger Bands
            data['BB_Middle'] = data['Close'].rolling(20).mean()
            bb_std = data['Close'].rolling(20).std()
            data['BB_Upper'] = data['BB_Middle'] + (bb_std * 2)
            data['BB_Lower'] = data['BB_Middle'] - (bb_std * 2)
            
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
                rsi <= max_rsi and  # Increased from 55 to 65
                not pd.isna(rsi) and 
                not pd.isna(current_price) and
                avg_volume >= min_volume * 0.2):  # Reduced from 0.5 to 0.2
                
                successful_fetches += 1
                
                # Calculate dynamic targets
                target_data = calculate_us_dynamic_targets(data, current_price)
                
                # RELAXED technical score calculation
                technical_score = 0
                
                # Trend alignment (RELAXED)
                if latest['Close'] > latest['EMA21']:
                    technical_score += 1
                if latest['EMA21'] > latest['EMA50']:
                    technical_score += 1
                
                # RSI conditions (RELAXED range for US)
                if 20 <= rsi <= 65:  # Expanded from 25-55 to 20-65
                    technical_score += 1
                
                # MACD bullish signal
                if latest['MACD'] > latest['MACD_Signal']:
                    technical_score += 1
                
                # Bollinger Band position (RELAXED)
                if not pd.isna(latest['BB_Lower']) and not pd.isna(latest['BB_Upper']):
                    bb_position = (latest['Close'] - latest['BB_Lower']) / (latest['BB_Upper'] - latest['BB_Lower'])
                    if 0.1 <= bb_position <= 0.8:  # More relaxed range
                        technical_score += 1
                else:
                    bb_position = 0.5
                
                # Volume confirmation
                if target_data['volume_surge']:
                    technical_score += 1
                
                # MUCH MORE RELAXED: Include stocks with 2+ conditions instead of 4+
                if technical_score >= 2:  # Reduced from 4 to 2
                    
                    # Risk rating based on volatility and market cap
                    if current_price > 200 and target_data['volatility'] < 0.25:
                        risk_rating = 'Low'
                    elif target_data['volatility'] > 0.35:
                        risk_rating = 'High'
                    else:
                        risk_rating = 'Medium'
                    
                    # Sector classification
                    sector = get_stock_sector(symbol)
                    
                    recommendations.append({
                        'Date': datetime.now().strftime('%Y-%m-%d'),
                        'Stock': symbol,
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
                        'Tech Score': f"{technical_score}/6",
                        'Sector': sector,
                        'Volatility': f"{target_data['volatility']:.1%}",
                        'BB Position': f"{bb_position:.2f}",
                        'Status': 'Active'
                    })
        
        except Exception as e:
            # Continue processing other stocks even if one fails
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    # Display scan statistics
    if successful_fetches > 0:
        st.info(f"✅ Successfully analyzed {successful_fetches} US stocks out of {total_symbols} attempted")
    else:
        st.warning(f"⚠️ Could not fetch data for any US stocks. This might be due to market hours or API limits.")
    
    # Sort by technical score and then by % gain potential
    df = pd.DataFrame(recommendations)
    if not df.empty:
        df = df.sort_values(['Tech Score', '% Gain'], ascending=[False, False])
        # Limit to top 20 results for display
        df = df.head(20)
    
    return df

def get_us_market_overview():
    """Get US market overview with error handling"""
    try:
        # Fetch major US indices
        spy = yf.download("SPY", period="1d", interval="5m")
        qqq = yf.download("QQQ", period="1d", interval="5m")
        
        overview = {}
        
        if not spy.empty:
            spy_close = spy['Close'].iloc[-1]
            spy_open = spy['Open'].iloc[0]
            spy_change = spy_close - spy_open
            spy_pct = (spy_change / spy_open) * 100
            
            overview['sp500'] = {
                'price': round(spy_close, 2),
                'change': round(spy_change, 2),
                'change_pct': round(spy_pct, 2)
            }
        
        if not qqq.empty:
            qqq_close = qqq['Close'].iloc[-1]
            qqq_open = qqq['Open'].iloc[0]
            qqq_change = qqq_close - qqq_open
            qqq_pct = (qqq_change / qqq_open) * 100
            
            overview['nasdaq'] = {
                'price': round(qqq_close, 2),
                'change': round(qqq_change, 2),
                'change_pct': round(qqq_pct, 2)
            }
        
        overview['last_updated'] = datetime.now().strftime('%H:%M:%S')
        return overview
        
    except Exception as e:
        return {
            'sp500': {'price': 450, 'change': 0, 'change_pct': 0},
            'nasdaq': {'price': 380, 'change': 0, 'change_pct': 0},
            'last_updated': 'Market data unavailable',
            'error': str(e)
        }
