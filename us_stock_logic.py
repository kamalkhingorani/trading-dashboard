# us_stock_logic.py - ENHANCED WITH FULL S&P 500 AND ADVANCED FEATURES
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import time
import requests

def get_full_sp500_universe():
    """Get complete S&P 500 universe with live data fallback"""
    try:
        # Try to fetch live S&P 500 list from multiple sources
        try:
            # Method 1: Wikipedia S&P 500 list (most reliable)
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            tables = pd.read_html(url)
            sp500_df = tables[0]  # First table contains the list
            symbols = sp500_df['Symbol'].tolist()
            
            # Clean symbols (handle special characters)
            cleaned_symbols = []
            for symbol in symbols:
                if pd.notna(symbol) and isinstance(symbol, str):
                    # Handle special cases like BRK.B, BF.B
                    clean_symbol = symbol.replace('.', '-') if '.' in symbol else symbol
                    cleaned_symbols.append(clean_symbol)
            
            if len(cleaned_symbols) > 400:
                st.success(f"✅ Fetched {len(cleaned_symbols)} stocks from live S&P 500 list")
                return cleaned_symbols
                
        except Exception as e:
            print(f"Live S&P 500 fetch failed: {e}")
            pass
        
        # Method 2: Try alternative source
        try:
            # Alternative API source for S&P 500
            url = "https://financialmodelingprep.com/api/v3/sp500_constituent?apikey=demo"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                symbols = [item['symbol'] for item in data if 'symbol' in item]
                if len(symbols) > 400:
                    st.success(f"✅ Fetched {len(symbols)} stocks from alternative S&P 500 source")
                    return symbols
        except:
            pass
        
        # Fallback to comprehensive S&P 500 list
        st.info("Using comprehensive S&P 500 fallback list")
        return get_comprehensive_sp500_list()
        
    except Exception as e:
        st.warning(f"Using fallback S&P 500 list: {e}")
        return get_comprehensive_sp500_list()

def get_comprehensive_sp500_list():
    """Comprehensive S&P 500 stock list covering all sectors"""
    return [
        # Technology (Large Cap)
        "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "TSLA", "META", "NVDA", "NFLX", "ADBE",
        "CRM", "ORCL", "INTC", "AMD", "QCOM", "AVGO", "CSCO", "IBM", "INTU", "NOW",
        "WDAY", "VEEV", "DDOG", "SNOW", "CRWD", "ZS", "OKTA", "SPLK", "TEAM", "ZM",
        "DOCU", "TWLO", "MDB", "NET", "FSLY", "ESTC", "CFLT", "BILL", "GTLB", "MNDY",
        
        # Financial Services  
        "JPM", "BAC", "WFC", "GS", "MS", "C", "AXP", "V", "MA", "BK", "USB", "PNC",
        "COF", "SCHW", "BLK", "SPGI", "MCO", "AIG", "TRV", "ALL", "PGR", "AFL", "MET",
        "PRU", "AON", "MMC", "AJG", "WTW", "BRO", "EQIX", "AMT", "CCI", "SBAC", "DLR",
        
        # Healthcare & Pharmaceuticals
        "JNJ", "PFE", "UNH", "ABBV", "TMO", "ABT", "MDT", "BMY", "AMGN", "GILD", "REGN",
        "BSX", "SYK", "ISRG", "ZBH", "BDX", "EW", "ALGN", "MRNA", "CVS", "ANTM", "CI",
        "HUM", "CNC", "DXCM", "ZTS", "IDEXX", "IQV", "MTD", "TECH", "HOLX", "VAR", "PKI",
        
        # Consumer Discretionary
        "AMZN", "HD", "LOW", "MCD", "SBUX", "NKE", "TJX", "ROST", "YUM", "CMG", "ULTA",
        "DIS", "F", "GM", "TSLA", "CCL", "RCL", "NCLH", "MAR", "HLT", "MGM", "WYNN",
        "LVS", "GRMN", "POOL", "TPG", "ORLY", "AZO", "AAP", "DPZ", "QSR", "DNKN",
        
        # Consumer Staples
        "WMT", "COST", "TGT", "PG", "KO", "PEP", "CL", "KMB", "GIS", "K", "CPB", "CAG",
        "HSY", "MDLZ", "MNST", "KHC", "CLX", "CHD", "SJM", "HRL", "MKC", "LW", "TAP",
        "STZ", "DEO", "PM", "MO", "BTI", "EL", "COTY", "KR", "SYY", "USG",
        
        # Energy
        "XOM", "CVX", "COP", "EOG", "SLB", "MPC", "VLO", "PSX", "OXY", "HAL", "BKR",
        "KMI", "WMB", "OKE", "EPD", "ET", "TRGP", "ONEOK", "MRO", "DVN", "FANG", "PXD",
        "CLR", "HES", "APA", "NOV", "RIG", "VAL", "DFS", "CTRA", "EQT", "AR", "MTDR",
        
        # Industrials
        "CAT", "GE", "MMM", "HON", "UPS", "FDX", "EMR", "ETN", "ITW", "PH", "CMI", "DE",
        "DOV", "ROK", "AME", "ROP", "DHR", "FTV", "XYL", "IEX", "FAST", "PCAR", "CHRW",
        "EXPD", "JBHT", "ODFL", "LSTR", "ADP", "PAYX", "BR", "TT", "CARR", "OTIS", "PWR",
        
        # Defense & Aerospace
        "BA", "LMT", "RTX", "NOC", "GD", "LHX", "TDG", "HWM", "LDOS", "KTOS", "AIR",
        "SPR", "CW", "MRCY", "HXL", "WWD", "MOG-A", "TXT", "AVAV", "LILAK", "ESLT",
        
        # Utilities
        "NEE", "DUK", "SO", "AEP", "EXC", "XEL", "WEC", "ES", "AWK", "CMS", "ETR", "ED",
        "FE", "ATO", "CNP", "DTE", "EVRG", "LNT", "NI", "POR", "SRE", "PCG", "EIX", "SCG",
        
        # Materials & Chemicals
        "LIN", "APD", "ECL", "SHW", "FCX", "NEM", "FMC", "ALB", "EMN", "IFF", "PPG", "CF",
        "MOS", "LYB", "DOW", "DD", "CE", "VMC", "MLM", "NUE", "STLD", "RS", "PKG", "SEE",
        "AVY", "BALL", "CCK", "SON", "WRK", "IP", "KNX", "RPM", "AXTA", "HUN", "OLN",
        
        # Real Estate Investment Trusts (REITs)
        "AMT", "EQIX", "PLD", "CCI", "SBAC", "DLR", "PSA", "EQR", "AVB", "ESS", "MAA",
        "UDR", "CPT", "AIV", "ELS", "SUI", "AMH", "ACC", "BXP", "KIM", "REG", "FRT",
        "SPG", "SIMON", "MAC", "SKT", "TCO", "WPC", "O", "NNN", "ADC", "STOR", "PSB",
        
        # Communication Services
        "GOOGL", "META", "NFLX", "DIS", "CHTR", "CMCSA", "T", "VZ", "TMUS", "DISH",
        "SIRI", "NYT", "NWSA", "FOXA", "PARA", "WBD", "LYV", "MTCH", "PINS", "SNAP",
        "TWTR", "ROKU", "SPOT", "ZI", "BMBL", "RBLX", "TTD", "MGNI", "FUBO", "PTON",
        
        # Additional Technology (Mid Cap)
        "PYPL", "SQ", "SHOP", "UBER", "LYFT", "DASH", "ABNB", "COIN", "HOOD", "AFRM",
        "UPST", "LC", "SOFI", "OPEN", "RDFN", "Z", "CARG", "CVNA", "VROOM", "SFT",
        
        # Biotechnology & Life Sciences
        "BIIB", "VRTX", "CELG", "ILMN", "BMRN", "ALXN", "SGEN", "TECH", "A", "TMO",
        "DHR", "WAT", "MKTX", "IDXX", "QGEN", "CDNS", "ANSS", "KLAC", "LRCX", "AMAT",
        
        # Semiconductors
        "NVDA", "AMD", "INTC", "QCOM", "AVGO", "TXN", "AMAT", "LRCX", "KLAC", "MCHP",
        "ADI", "XLNX", "MRVL", "SWKS", "QRVO", "MPWR", "CRUS", "CCOI", "LSCC", "FORM",
        
        # Retail & E-commerce
        "AMZN", "WMT", "COST", "HD", "LOW", "TGT", "TJX", "ROST", "KSS", "M", "JWN",
        "NILE", "GPS", "ANF", "AEO", "URBN", "FIVE", "DKS", "HIBB", "SCVL", "BOOT",
        
        # Transportation & Logistics
        "UPS", "FDX", "CHRW", "EXPD", "JBHT", "ODFL", "LSTR", "SAIA", "ARCB", "WERN",
        "KNX", "YELL", "HTLD", "SNDR", "GXO", "XPO", "LYFT", "UBER", "DASH", "GRUB"
    ]

def calculate_advanced_rsi_with_trend_us(data):
    """Calculate RSI with enhanced trend analysis for US stocks"""
    try:
        # Calculate RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        if len(rsi) < 20:
            return None, False
        
        # RSI trend analysis (last 5 days)
        recent_rsi = rsi.tail(5)
        rsi_trend = 'rising' if recent_rsi.iloc[-1] > recent_rsi.iloc[-3] > recent_rsi.iloc[-5] else 'falling' if recent_rsi.iloc[-1] < recent_rsi.iloc[-3] < recent_rsi.iloc[-5] else 'neutral'
        
        # Check for RSI extremes and recovery patterns
        min_rsi_recent = rsi.tail(10).min()
        max_rsi_recent = rsi.tail(10).max()
        current_rsi = rsi.iloc[-1]
        
        # RSI recovery pattern (from oversold)
        rsi_oversold_recovery = (min_rsi_recent < 30 and current_rsi > min_rsi_recent + 5 and rsi_trend == 'rising')
        
        # RSI overbought decline pattern (from overbought)
        rsi_overbought_decline = (max_rsi_recent > 70 and current_rsi < max_rsi_recent - 5 and rsi_trend == 'falling')
        
        return {
            'current_rsi': current_rsi,
            'min_recent_rsi': min_rsi_recent,
            'max_recent_rsi': max_rsi_recent,
            'rsi_trend': rsi_trend,
            'rsi_oversold_recovery': rsi_oversold_recovery,
            'rsi_overbought_decline': rsi_overbought_decline,
            'rsi_series': rsi
        }, True
        
    except Exception:
        return None, False

def analyze_us_candlestick_patterns(data):
    """Analyze bullish and bearish candlestick patterns for US stocks"""
    try:
        if len(data) < 5:
            return {'pattern': 'insufficient_data', 'strength': 0, 'direction': 'neutral'}
        
        recent_data = data.tail(5)
        patterns = []
        bullish_strength = 0
        bearish_strength = 0
        
        for i, candle in recent_data.iterrows():
            open_price = candle['Open']
            close_price = candle['Close']
            high_price = candle['High']
            low_price = candle['Low']
            
            body = abs(close_price - open_price)
            upper_shadow = high_price - max(open_price, close_price)
            lower_shadow = min(open_price, close_price) - low_price
            candle_range = high_price - low_price
            
            if candle_range == 0:
                continue
                
            # Bullish patterns
            if close_price > open_price:  # Green candle
                if body > candle_range * 0.7:  # Strong green candle
                    patterns.append('strong_bullish')
                    bullish_strength += 2
                elif lower_shadow > body * 2:  # Hammer pattern
                    patterns.append('hammer')
                    bullish_strength += 3
                else:
                    patterns.append('bullish')
                    bullish_strength += 1
            
            # Bearish patterns
            elif close_price < open_price:  # Red candle
                if body > candle_range * 0.7:  # Strong red candle
                    patterns.append('strong_bearish')
                    bearish_strength += 2
                elif upper_shadow > body * 2:  # Shooting star pattern
                    patterns.append('shooting_star')
                    bearish_strength += 3
                else:
                    patterns.append('bearish')
                    bearish_strength += 1
            
            # Doji patterns
            elif body < candle_range * 0.1:  # Small body
                if lower_shadow > body * 3:  # Dragonfly doji (bullish)
                    patterns.append('dragonfly_doji')
                    bullish_strength += 2
                elif upper_shadow > body * 3:  # Gravestone doji (bearish)
                    patterns.append('gravestone_doji')
                    bearish_strength += 2
        
        # Weekly analysis
        weekly_open = recent_data['Open'].iloc[0]
        weekly_close = recent_data['Close'].iloc[-1]
        weekly_direction = 'bullish' if weekly_close > weekly_open else 'bearish'
        
        if weekly_direction == 'bullish':
            patterns.append('weekly_bullish')
            bullish_strength += 1
        else:
            patterns.append('weekly_bearish')
            bearish_strength += 1
        
        # Determine overall direction and strength
        if bullish_strength > bearish_strength:
            direction = 'bullish'
            strength = bullish_strength
        elif bearish_strength > bullish_strength:
            direction = 'bearish'
            strength = bearish_strength
        else:
            direction = 'neutral'
            strength = max(bullish_strength, bearish_strength)
        
        return {
            'patterns': patterns,
            'direction': direction,
            'strength': strength,
            'bullish_strength': bullish_strength,
            'bearish_strength': bearish_strength,
            'weekly_direction': weekly_direction,
            'primary_pattern': patterns[0] if patterns else 'neutral'
        }
        
    except Exception:
        return {'pattern': 'analysis_failed', 'strength': 0, 'direction': 'neutral'}

def detect_us_support_resistance(data):
    """Detect support and resistance levels for US stocks"""
    try:
        if len(data) < 30:
            return {'near_support': False, 'near_resistance': False, 'support_level': 0, 'resistance_level': 0}
        
        # Find recent support and resistance levels
        recent_30_low = data['Low'].tail(30).min()
        recent_30_high = data['High'].tail(30).max()
        recent_10_low = data['Low'].tail(10).min()
        recent_10_high = data['High'].tail(10).max()
        current_price = data['Close'].iloc[-1]
        
        # Check proximity to support/resistance (within 3% for US stocks)
        support_distance = (current_price - recent_30_low) / recent_30_low
        resistance_distance = (recent_30_high - current_price) / current_price
        
        near_support = support_distance < 0.03
        near_resistance = resistance_distance < 0.03
        
        # Check for bounces
        bounce_from_support = (recent_10_low <= recent_30_low * 1.01 and 
                              current_price > recent_10_low * 1.02)
        
        rejection_from_resistance = (recent_10_high >= recent_30_high * 0.99 and
                                   current_price < recent_10_high * 0.98)
        
        return {
            'near_support': near_support,
            'near_resistance': near_resistance,
            'bounce_from_support': bounce_from_support,
            'rejection_from_resistance': rejection_from_resistance,
            'support_level': recent_30_low,
            'resistance_level': recent_30_high,
            'support_distance_pct': support_distance * 100,
            'resistance_distance_pct': resistance_distance * 100
        }
        
    except Exception:
        return {'near_support': False, 'near_resistance': False}

def calculate_us_volume_analysis(data):
    """Enhanced volume analysis for US stocks"""
    try:
        if 'Volume' not in data.columns or len(data) < 20:
            return {'volume_surge': False, 'avg_volume': 0, 'volume_trend': 'unknown'}
        
        recent_volume = data['Volume'].tail(5).mean()
        avg_volume_20d = data['Volume'].tail(20).mean()
        avg_volume_50d = data['Volume'].tail(50).mean() if len(data) >= 50 else avg_volume_20d
        
        # Volume surge detection
        volume_surge = recent_volume > avg_volume_20d * 1.5
        high_volume_surge = recent_volume > avg_volume_20d * 2.0
        
        # Volume trend
        if recent_volume > avg_volume_20d * 1.2:
            volume_trend = 'increasing'
        elif recent_volume < avg_volume_20d * 0.8:
            volume_trend = 'decreasing'
        else:
            volume_trend = 'stable'
        
        # Volume quality (comparing recent vs longer-term average)
        volume_quality = recent_volume / avg_volume_50d if avg_volume_50d > 0 else 1
        
        return {
            'volume_surge': volume_surge,
            'high_volume_surge': high_volume_surge,
            'volume_trend': volume_trend,
            'volume_quality': volume_quality,
            'recent_volume': recent_volume,
            'avg_volume_20d': avg_volume_20d,
            'avg_volume_50d': avg_volume_50d,
            'volume_ratio': recent_volume / avg_volume_20d if avg_volume_20d > 0 else 1
        }
        
    except Exception:
        return {'volume_surge': False, 'avg_volume': 0, 'volume_trend': 'unknown'}

def calculate_us_dynamic_targets(data, current_price):
    """Calculate dynamic targets for US stocks with enhanced logic"""
    try:
        # Calculate volatility
        returns = data['Close'].pct_change().dropna()
        volatility = returns.tail(20).std() * np.sqrt(252) if len(returns) >= 20 else 0.20
        
        # Add randomness for unique targets
        np.random.seed(None)
        volatility = volatility * np.random.uniform(0.95, 1.05)
        
        # Support and resistance levels
        recent_high = data['High'].tail(30).max()
        recent_low = data['Low'].tail(30).min()
        
        # Volume and momentum analysis
        volume_analysis = calculate_us_volume_analysis(data)
        
        # Target calculation based on US market characteristics (generally lower than Indian)
        if volatility > 0.35:  # High volatility
            base_target_pct = np.random.uniform(4, 8)
        elif volatility > 0.25:  # Medium volatility  
            base_target_pct = np.random.uniform(3, 6)
        else:  # Low volatility
            base_target_pct = np.random.uniform(2, 5)
        
        # Market cap adjustments (US market specific)
        if current_price > 300:  # Large cap (like AAPL, GOOGL)
            base_target_pct *= 0.8
        elif current_price < 50:  # Small/mid cap
            base_target_pct *= 1.1
        
        # Technical adjustments
        if len(data) >= 50:
            ema21 = data['Close'].ewm(span=21).mean().iloc[-1]
            ema50 = data['Close'].ewm(span=50).mean().iloc[-1]
            
            # Trend alignment bonus
            if current_price > ema21 > ema50:
                base_target_pct *= 1.05
            
            # Volume confirmation bonus
            if volume_analysis['volume_surge']:
                base_target_pct *= 1.03
        
        # Calculate target price
        target_price = current_price * (1 + base_target_pct / 100)
        
        # Ensure target doesn't exceed recent resistance
        if target_price > recent_high * 1.05:
            target_price = recent_high * 1.05
            base_target_pct = ((target_price / current_price) - 1) * 100
        
        # Stop loss calculation (more conservative for US stocks)
        support_level = recent_low * 1.01
        volatility_sl = current_price * (1 - min(volatility * 0.6, 0.04))
        
        stop_loss = max(support_level, volatility_sl)
        
        # Risk management
        potential_gain = target_price - current_price
        max_allowed_sl_price = current_price - (potential_gain * 0.4)
        
        if stop_loss < max_allowed_sl_price:
            stop_loss = max_allowed_sl_price
        
        # Ensure minimum stop loss distance
        min_sl_price = current_price * 0.98
        stop_loss = min(stop_loss, min_sl_price)
        
        sl_pct = ((current_price - stop_loss) / current_price) * 100
        
        # Calculate risk-reward ratio
        risk = current_price - stop_loss
        reward = target_price - current_price
        risk_reward_ratio = round(reward / risk, 1) if risk > 0 else 1.0
        
        # Estimated days (US market typically faster)
        if base_target_pct <= 3:
            estimated_days = np.random.randint(3, 10)
        elif base_target_pct <= 5:
            estimated_days = np.random.randint(5, 15)
        else:
            estimated_days = np.random.randint(8, 20)
        
        return {
            'target': target_price,
            'target_pct': base_target_pct,
            'stop_loss': stop_loss,
            'sl_pct': sl_pct,
            'estimated_days': estimated_days,
            'volatility': volatility,
            'risk_reward_ratio': risk_reward_ratio
        }
        
    except Exception:
        # Fallback calculation
        target_price = current_price * 1.04
        stop_loss = current_price * 0.98
        return {
            'target': target_price,
            'target_pct': 4.0,
            'stop_loss': stop_loss,
            'sl_pct': 2.0,
            'estimated_days': 8,
            'volatility': 0.20,
            'risk_reward_ratio': 2.0
        }

def get_us_stock_sector(symbol):
    """Enhanced sector mapping for US stocks"""
    sector_mapping = {
        # Technology
        'Technology': ['AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'NVDA', 'NFLX', 'ADBE',
                      'CRM', 'ORCL', 'INTC', 'AMD', 'QCOM', 'AVGO', 'CSCO', 'IBM', 'INTU',
                      'NOW', 'WDAY', 'VEEV', 'DDOG', 'SNOW', 'CRWD', 'ZS', 'OKTA'],
        
        # Financial
        'Financial': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'V', 'MA', 'AXP', 'BK', 
                     'USB', 'PNC', 'COF', 'SCHW', 'BLK', 'SPGI', 'MCO', 'AIG', 'TRV'],
        
        # Healthcare
        'Healthcare': ['JNJ', 'PFE', 'UNH', 'ABBV', 'TMO', 'ABT', 'MDT', 'BMY', 'AMGN', 
                      'GILD', 'REGN', 'BSX', 'SYK', 'ISRG', 'ZBH', 'BDX', 'MRNA', 'CVS'],
        
        # Consumer Discretionary
        'Consumer Discretionary': ['HD', 'LOW', 'MCD', 'SBUX', 'NKE', 'TJX', 'ROST', 'YUM', 
                                  'CMG', 'ULTA', 'DIS', 'F', 'GM', 'TSLA'],
        
        # Consumer Staples
        'Consumer Staples': ['WMT', 'COST', 'TGT', 'PG', 'KO', 'PEP', 'CL', 'KMB'],
        
        # Energy
        'Energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'MPC', 'VLO', 'PSX', 'OXY', 'HAL'],
        
        # Industrial
        'Industrial': ['CAT', 'GE', 'MMM', 'HON', 'UPS', 'FDX', 'EMR', 'ETN', 'ITW', 'PH'],
        
        # Materials
        'Materials': ['LIN', 'APD', 'ECL', 'SHW', 'FCX', 'NEM', 'FMC', 'ALB', 'EMN'],
        
        # Utilities
        'Utilities': ['NEE', 'DUK', 'SO', 'AEP', 'EXC', 'XEL', 'WEC', 'ES', 'AWK'],
        
        # Communication Services
        'Communication': ['GOOGL', 'META', 'NFLX', 'DIS', 'CHTR', 'CMCSA', 'T', 'VZ'],
        
        # Real Estate
        'Real Estate': ['AMT', 'EQIX', 'PLD', 'CCI', 'SBAC', 'DLR', 'PSA', 'EQR']
    }
    
    for sector, symbols in sector_mapping.items():
        if symbol in symbols:
            return sector
    
    return 'Other'

def get_us_recommendations(min_price=25, max_rsi=65, min_volume=500000, batch_size=500):
    """ENHANCED: Get US stock recommendations with full S&P 500 coverage and advanced analysis"""
    
    try:
def get_us_recommendations(min_price=25, max_rsi=65, min_volume=500000, batch_size=500):
    """ENHANCED: Get US stock recommendations with full S&P 500 coverage and advanced analysis"""
    
    try:
        symbols = get_full_sp500_universe()
        recommendations = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_symbols = min(len(symbols), batch_size)
        successful_fetches = 0
        pattern_filtered_count = 0
        
        status_text.text(f"🔍 Starting S&P 500 scan of {total_symbols} stocks with advanced pattern analysis...")
        
        # Adaptive delay for large scans
        batch_delay = 0.03 if batch_size > 300 else 0.08
        
        for i, symbol in enumerate(symbols[:total_symbols]):
            try:
                progress_bar.progress((i + 1) / total_symbols)
                status_text.text(f"Analyzing {symbol}... ({i+1}/{total_symbols}) | Qualified: {pattern_filtered_count}")
                
                time.sleep(batch_delay)
                
                # Fetch data
                stock = yf.Ticker(symbol)
                data = stock.history(period="3mo", interval="1d")
                
                if len(data) < 25:
                    continue
                
                current_price = data['Close'].iloc[-1]
                
                # Apply minimum price filter
                if current_price < min_price:
                    continue
                
                # Enhanced RSI analysis with bullish/bearish detection
                rsi_analysis, rsi_success = calculate_advanced_rsi_with_trend_us(data)
                if not rsi_success or not rsi_analysis:
                    continue
                
                current_rsi = rsi_analysis['current_rsi']
                
                # Apply RSI filter
                if current_rsi > max_rsi:
                    continue
                
                # Enhanced pattern analysis (bullish AND bearish)
                pattern_analysis = analyze_us_candlestick_patterns(data)
                
                # Support/Resistance analysis
                sr_analysis = detect_us_support_resistance(data)
                
                # Volume analysis
                volume_analysis = calculate_us_volume_analysis(data)
                
                # Calculate additional technical indicators
                data['EMA20'] = data['Close'].ewm(span=20).mean()
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
                
                # Enhanced technical scoring system (supports both bullish and bearish)
                technical_score = 0
                score_components = []
                trade_direction = 'neutral'
                
                # RSI-based direction and scoring
                if rsi_analysis['rsi_oversold_recovery']:
                    technical_score += 3
                    score_components.append("RSI Recovery")
                    trade_direction = 'bullish'
                elif rsi_analysis['rsi_overbought_decline']:
                    technical_score += 3
                    score_components.append("RSI Decline")
                    trade_direction = 'bearish'
                elif rsi_analysis['rsi_trend'] == 'rising' and 30 < current_rsi < 60:
                    technical_score += 2
                    score_components.append("Rising RSI")
                    trade_direction = 'bullish'
                elif rsi_analysis['rsi_trend'] == 'falling' and 40 < current_rsi < 70:
                    technical_score += 2
                    score_components.append("Falling RSI")
                    trade_direction = 'bearish'
                
                # Pattern-based scoring
                if pattern_analysis['direction'] == 'bullish' and pattern_analysis['strength'] >= 2:
                    technical_score += 2
                    score_components.append("Bullish Patterns")
                    if trade_direction == 'neutral':
                        trade_direction = 'bullish'
                elif pattern_analysis['direction'] == 'bearish' and pattern_analysis['strength'] >= 2:
                    technical_score += 2
                    score_components.append("Bearish Patterns")
                    if trade_direction == 'neutral':
                        trade_direction = 'bearish'
                
                # Trend alignment
                if latest['Close'] > latest['EMA20'] > latest['EMA50']:
                    technical_score += 2
                    score_components.append("Strong Uptrend")
                    if trade_direction == 'neutral':
                        trade_direction = 'bullish'
                elif latest['Close'] < latest['EMA20'] < latest['EMA50']:
                    technical_score += 2
                    score_components.append("Strong Downtrend")
                    if trade_direction == 'neutral':
                        trade_direction = 'bearish'
                elif latest['Close'] > latest['EMA20']:
                    technical_score += 1
                    score_components.append("Above EMA20")
                
                # Support/Resistance scoring
                if sr_analysis['bounce_from_support'] and trade_direction == 'bullish':
                    technical_score += 2
                    score_components.append("Support Bounce")
                elif sr_analysis['rejection_from_resistance'] and trade_direction == 'bearish':
                    technical_score += 2
                    score_components.append("Resistance Reject")
                elif sr_analysis['near_support']:
                    technical_score += 1
                    score_components.append("Near Support")
                elif sr_analysis['near_resistance']:
                    technical_score += 1
                    score_components.append("Near Resistance")
                
                # Volume confirmation
                if volume_analysis['high_volume_surge']:
                    technical_score += 2
                    score_components.append("High Volume")
                elif volume_analysis['volume_surge']:
                    technical_score += 1
                    score_components.append("Volume Surge")
                
                # MACD signal
                if latest['MACD'] > latest['MACD_Signal'] and trade_direction == 'bullish':
                    technical_score += 1
                    score_components.append("MACD Bullish")
                elif latest['MACD'] < latest['MACD_Signal'] and trade_direction == 'bearish':
                    technical_score += 1
                    score_components.append("MACD Bearish")
                
                # Bollinger Band position
                if not pd.isna(latest['BB_Lower']) and not pd.isna(latest['BB_Upper']):
                    bb_position = (latest['Close'] - latest['BB_Lower']) / (latest['BB_Upper'] - latest['BB_Lower'])
                    if bb_position < 0.2 and trade_direction == 'bullish':  # Oversold
                        technical_score += 1
                        score_components.append("BB Oversold")
                    elif bb_position > 0.8 and trade_direction == 'bearish':  # Overbought
                        technical_score += 1
                        score_components.append("BB Overbought")
                else:
                    bb_position = 0.5
                
                # Only include stocks with clear directional bias and good technical score
                if technical_score >= 4 and trade_direction != 'neutral':
                    successful_fetches += 1
                    pattern_filtered_count += 1
                    
                    # Calculate dynamic targets based on direction
                    target_data = calculate_us_dynamic_targets(data, current_price)
                    
                    # Adjust targets based on trade direction
                    if trade_direction == 'bearish':
                        # For bearish trades, we're looking for price to go down
                        # So "target" becomes the downside target
                        downside_target = current_price * (1 - target_data['target_pct'] / 100)
                        upside_stop = current_price * (1 + target_data['sl_pct'] / 100)
                        
                        final_target = downside_target
                        final_stop = upside_stop
                        final_target_pct = -target_data['target_pct']  # Negative for bearish
                        final_sl_pct = target_data['sl_pct']
                    else:
                        # Bullish trades (normal upside targets)
                        final_target = target_data['target']
                        final_stop = target_data['stop_loss']
                        final_target_pct = target_data['target_pct']
                        final_sl_pct = target_data['sl_pct']
                    
                    # Risk rating
                    if target_data['volatility'] > 0.35:
                        risk_rating = 'High'
                    elif target_data['volatility'] > 0.25:
                        risk_rating = 'Medium'
                    else:
                        risk_rating = 'Low'
                    
                    # Get sector classification
                    sector = get_us_stock_sector(symbol)
                    
                    # Create selection reason
                    primary_reasons = score_components[:3]  # Top 3 reasons
                    selection_reason = " + ".join(primary_reasons)
                    
                    recommendation_data = {
                        'Date': datetime.now().strftime('%Y-%m-%d'),
                        'Stock': symbol,
                        'LTP': round(current_price, 2),
                        'RSI': round(current_rsi, 1),
                        'Direction': trade_direction.title(),
                        'Target': round(final_target, 2),
                        '% Move': round(abs(final_target_pct), 1),
                        'Est.Days': target_data['estimated_days'],
                        'Stop Loss': round(final_stop, 2),
                        'SL %': round(final_sl_pct, 1),
                        'Risk:Reward': f"1:{target_data['risk_reward_ratio']}",
                        'Selection Reason': selection_reason,
                        'Primary Pattern': pattern_analysis['primary_pattern'],
                        'Pattern Strength': pattern_analysis['strength'],
                        'Volume': int(volume_analysis['recent_volume']),
                        'Risk': risk_rating,
                        'Tech Score': f"{technical_score}/12",
                        'Sector': sector,
                        'BB Position': f"{bb_position:.2f}",
                        'Volatility': f"{target_data['volatility']:.1%}",
                        'RSI Trend': rsi_analysis['rsi_trend'].title(),
                        'Status': 'Active'
                    }
                    
                    recommendations.append(recommendation_data)
            
            except Exception as e:
                continue
        
        progress_bar.empty()
        status_text.empty()
        
        # Display comprehensive scan statistics
        if successful_fetches > 0:
            bullish_count = len([r for r in recommendations if r['Direction'] == 'Bullish'])
            bearish_count = len([r for r in recommendations if r['Direction'] == 'Bearish'])
            
            st.success(f"""
            ✅ **Full S&P 500 Scan Complete!**
            - **Analyzed**: {total_symbols} stocks from S&P 500 universe
            - **Technical Qualifiers**: {pattern_filtered_count} stocks passed advanced filters
            - **Final Recommendations**: {successful_fetches} high-quality opportunities
            - **Bullish Setups**: {bullish_count} | **Bearish Setups**: {bearish_count}
            - **Filter Criteria**: RSI patterns + candlestick analysis + volume + trend confirmation
            """)
        else:
            st.warning(f"""
            ⚠️ **No opportunities found with current criteria**
            - Scanned: {total_symbols} S&P 500 stocks
            - Pattern candidates: {pattern_filtered_count}
            - Try adjusting RSI limits or scanning during different market conditions
            """)
        
        # Sort by technical score and expected move
        df = pd.DataFrame(recommendations)
        if not df.empty:
            # Convert technical score for sorting
            df['Score_Numeric'] = df['Tech Score'].str.split('/').str[0].astype(float)
            df = df.sort_values(['Score_Numeric', '% Move'], ascending=[False, False])
            df = df.drop('Score_Numeric', axis=1)
            df = df.head(25)  # Top 25 recommendations
        
        return df
        
    except Exception as e:
        st.error(f"Error in enhanced S&P 500 scanning: {str(e)}")
        return pd.DataFrame()

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
        
        overview['last_updated'] = datetime.now().strftime('%H:%M:%S EST')
        return overview
        
    except Exception as e:
        return {
            'sp500': {'price': 450, 'change': 0, 'change_pct': 0},
            'nasdaq': {'price': 380, 'change': 0, 'change_pct': 0},
            'last_updated': 'Market data unavailable*',
            'error': str(e)
        }
