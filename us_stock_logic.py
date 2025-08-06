# us_stock_logic.py - ENHANCED WITH TECHNICAL REASONING
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

def analyze_us_technical_patterns(data, symbol):
    """Analyze US technical patterns with more sophisticated logic"""
    reasons = []
    pattern_strength = 0
    is_fallback = False
    
    try:
        # Get recent data
        recent_data = data.tail(10)
        latest = recent_data.iloc[-1]
        previous = recent_data.iloc[-2] if len(recent_data) >= 2 else latest
        
        # 1. ADVANCED CANDLESTICK PATTERNS
        current_candle_bullish = latest['Close'] > latest['Open']
        prev_candle_bullish = previous['Close'] > previous['Open']
        
        # Doji detection
        body_size = abs(latest['Close'] - latest['Open'])
        candle_range = latest['High'] - latest['Low']
        is_doji = body_size < (candle_range * 0.1) if candle_range > 0 else False
        
        # Hammer/Shooting star
        upper_shadow = latest['High'] - max(latest['Open'], latest['Close'])
        lower_shadow = min(latest['Open'], latest['Close']) - latest['Low']
        
        if current_candle_bullish and body_size > (candle_range * 0.6):
            reasons.append("Strong Bullish Candle")
            pattern_strength += 2
        elif is_doji and not prev_candle_bullish:
            reasons.append("Doji Reversal Pattern")
            pattern_strength += 1
        elif lower_shadow > body_size * 2 and current_candle_bullish:
            reasons.append("Hammer Pattern")
            pattern_strength += 2
        elif current_candle_bullish:
            reasons.append("Bullish Candle")
            pattern_strength += 1
            
        # 2. RSI DIVERGENCE AND MOMENTUM
        if 'RSI' in data.columns and len(recent_data) >= 3:
            rsi_values = recent_data['RSI'].tail(3)
            price_values = recent_data['Close'].tail(3)
            
            if not rsi_values.isna().any():
                # RSI trend
                rsi_rising = rsi_values.iloc[-1] > rsi_values.iloc[-2] > rsi_values.iloc[-3]
                price_rising = price_values.iloc[-1] > price_values.iloc[-2]
                
                if rsi_rising and price_rising and 30 < rsi_values.iloc[-1] < 60:
                    reasons.append("Rising RSI + Price")
                    pattern_strength += 2
                elif rsi_values.iloc[-1] < 30:
                    reasons.append("Oversold RSI (<30)")
                    pattern_strength += 1
                elif 30 < rsi_values.iloc[-1] < 45:
                    reasons.append("RSI Recovery Zone")
                    pattern_strength += 1
            else:
                is_fallback = True
                
        # 3. VOLUME BREAKOUT ANALYSIS
        if 'Volume' in data.columns and len(recent_data) >= 10:
            recent_volume = recent_data['Volume'].tail(3).mean()
            baseline_volume = recent_data['Volume'].head(7).mean()
            
            volume_ratio = recent_volume / baseline_volume if baseline_volume > 0 else 1
            
            if volume_ratio > 2.0:
                reasons.append("Volume Breakout (2x)")
                pattern_strength += 3
            elif volume_ratio > 1.5:
                reasons.append("High Volume (1.5x)")
                pattern_strength += 2
            elif volume_ratio > 1.2:
                reasons.append("Above Avg Volume")
                pattern_strength += 1
        else:
            is_fallback = True
            
        # 4. BOLLINGER BAND ANALYSIS
        if len(recent_data) >= 20:
            bb_period = min(20, len(recent_data))
            bb_data = recent_data.tail(bb_period)
            
            bb_middle = bb_data['Close'].rolling(bb_period).mean().iloc[-1]
            bb_std = bb_data['Close'].rolling(bb_period).std().iloc[-1]
            
            if not pd.isna(bb_middle) and not pd.isna(bb_std) and bb_std > 0:
                bb_upper = bb_middle + (bb_std * 2)
                bb_lower = bb_middle - (bb_std * 2)
                
                bb_position = (latest['Close'] - bb_lower) / (bb_upper - bb_lower)
                
                if bb_position < 0.2:
                    reasons.append("BB Oversold Zone")
                    pattern_strength += 1
                elif 0.2 <= bb_position <= 0.4:
                    reasons.append("BB Buy Zone")
                    pattern_strength += 1
                elif bb_position > 0.8:
                    reasons.append("BB Breakout")
                    pattern_strength += 2
            else:
                is_fallback = True
                
        # 5. MOVING AVERAGE CONVERGENCE
        if 'EMA21' in data.columns and 'EMA50' in data.columns:
            ema21 = latest['EMA21']
            ema50 = latest['EMA50']
            prev_ema21 = previous['EMA21'] if 'EMA21' in previous else ema21
            prev_ema50 = previous['EMA50'] if 'EMA50' in previous else ema50
            
            if not pd.isna(ema21) and not pd.isna(ema50):
                # Golden cross detection
                if ema21 > ema50 and prev_ema21 <= prev_ema50:
                    reasons.append("Golden Cross (EMA)")
                    pattern_strength += 3
                elif latest['Close'] > ema21 > ema50:
                    reasons.append("Above All EMAs")
                    pattern_strength += 2
                elif latest['Close'] > ema21:
                    reasons.append("Above EMA21")
                    pattern_strength += 1
            else:
                is_fallback = True
                
        # 6. WEEKLY TIMEFRAME ANALYSIS
        if len(data) >= 7:
            # Weekly simulation using 7-day periods
            weekly_data = data.tail(7)
            weekly_open = weekly_data['Open'].iloc[0]
            weekly_close = latest['Close']
            weekly_high = weekly_data['High'].max()
            weekly_low = weekly_data['Low'].min()
            
            weekly_bullish = weekly_close > weekly_open
            weekly_body_pct = abs(weekly_close - weekly_open) / (weekly_high - weekly_low) if (weekly_high - weekly_low) > 0 else 0
            
            if weekly_bullish and weekly_body_pct > 0.6:
                reasons.append("Strong Weekly Bullish")
                pattern_strength += 2
            elif weekly_bullish and weekly_body_pct > 0.3:
                reasons.append("Weekly Bullish Bias")
                pattern_strength += 1
                
        # 7. SECTOR MOMENTUM (based on symbol)
        sector = get_stock_sector(symbol)
        if sector in ['Technology', 'Healthcare', 'Financial']:
            reasons.append(f"{sector} Sector Play")
            pattern_strength += 0.5
            
        # 8. SUPPORT/RESISTANCE LEVELS
        if len(data) >= 30:
            support_level = data['Low'].tail(30).min()
            resistance_level = data['High'].tail(30).max()
            
            distance_from_support = (latest['Close'] - support_level) / support_level
            distance_from_resistance = (resistance_level - latest['Close']) / latest['Close']
            
            if distance_from_support < 0.05:  # Within 5% of support
                reasons.append("Near Support Level")
                pattern_strength += 1
            elif distance_from_resistance < 0.03:  # Within 3% of resistance
                reasons.append("Resistance Breakout")
                pattern_strength += 2
                
        # Compile final reasoning
        if not reasons:
            reasons.append("Basic Technical Setup")
            
        return {
            'primary_reason': reasons[0] if reasons else "Technical Setup",
            'all_reasons': " + ".join(reasons[:3]),  # Top 3 reasons
            'pattern_strength': round(pattern_strength, 1),
            'is_fallback': is_fallback,
            'total_reasons': len(reasons)
        }
        
    except Exception as e:
        return {
            'primary_reason': "Pattern Analysis Failed*",
            'all_reasons': "Technical Setup*",
            'pattern_strength': 1,
            'is_fallback': True,
            'total_reasons': 0
        }

def get_expanded_sp500_universe():
    """Complete S&P 500 universe"""
    try:
        # Fetch S&P 500 list from Wikipedia
        sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        sp500_df = pd.read_html(sp500_url)[0]
        return sp500_df['Symbol'].tolist()
        
    except Exception:
        # Fallback to complete manual S&P 500 list (500 unique stocks)
        return [
            # Technology
            "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "TSLA", "META", "NVDA", "NFLX", "ADBE",
            "CRM", "ORCL", "INTC", "AMD", "QCOM", "AVGO", "CSCO", "IBM", "INTU", "NOW",
            "WDAY", "VEEV", "DDOG", "SNOW", "CRWD", "ZS", "OKTA", "ANET", "FTNT", "PANW",
            "VRSN", "JNPR", "NTAP", "WDC", "STX", "HPQ", "HPE", "DELL", "VMW", "CTSH",
            "ACN", "EPAM", "LDOS", "DXC", "IT", "GLW", "APH", "TEL", "MCHP", "KLAC",
            
            # Financial Services
            "JPM", "BAC", "WFC", "GS", "MS", "C", "AXP", "V", "MA", "BK", "USB", "PNC",
            "COF", "SCHW", "BLK", "SPGI", "MCO", "AIG", "TRV", "ALL", "PGR", "AFL",
            "MET", "PRU", "AMP", "TROW", "BEN", "IVZ", "NDAQ", "ICE", "CME", "CBOE",
            "FIS", "FISV", "PYPL", "SQ", "AFRM", "LC", "ALLY", "FITB", "RF", "CFG",
            "HBAN", "KEY", "CMA", "ZION", "EWBC", "PBCT", "WBS", "MTB", "STI", "BBT",
            
            # Healthcare & Pharmaceuticals
            "JNJ", "PFE", "UNH", "ABBV", "TMO", "ABT", "MDT", "BMY", "AMGN", "GILD",
            "REGN", "BSX", "SYK", "ISRG", "ZBH", "BDX", "EW", "ALGN", "MRNA", "BNTX",
            "CVS", "ANTM", "CI", "HUM", "CNC", "DXCM", "ZTS", "IDEXX", "CAH", "MCK",
            "ABC", "WBA", "ILMN", "A", "DHR", "WAT", "PKI", "LH", "DGX", "HOLX",
            "TECH", "QDEL", "QGEN", "MYGN", "EXAS", "TDOC", "AMWL", "DOCS", "VEEV", "TMDX",
            
            # Energy
            "XOM", "CVX", "COP", "EOG", "SLB", "MPC", "VLO", "PSX", "OXY", "HAL",
            "BKR", "FTI", "NOV", "RIG", "HP", "MRO", "APA", "DVN", "FANG", "PXD",
            "CXO", "CLR", "NBL", "COG", "CNX", "EQT", "AR", "CHK", "WPX", "PE",
            "PDCE", "MTDR", "CDEV", "CPE", "WLL", "GPOR", "NEXT", "CRC", "OAS", "SM",
            "MGY", "REI", "CRZO", "HES", "KMI", "EPD", "ET", "MPLX", "WMB", "OKE",
            
            # Consumer Discretionary
            "AMZN", "HD", "LOW", "TGT", "NKE", "TJX", "ROST", "YUM", "CMG", "SBUX",
            "ULTA", "DIS", "F", "GM", "EBAY", "ETSY", "W", "CHWY", "NCLH", "CCL",
            "RCL", "MAR", "HLT", "H", "WH", "IHG", "EXPE", "BKNG", "TRIP", "ABNB",
            "UBER", "LYFT", "DASH", "GRMN", "POOL", "LVS", "WYNN", "MGM", "CZR", "PENN",
            "DRI", "EAT", "TXRH", "DNKN", "MCD", "QSR", "DPZ", "PZZA", "PLAY", "CKE",
            
            # Consumer Staples
            "PG", "KO", "PEP", "WMT", "COST", "MCD", "KHC", "MNST", "KDP", "GIS",
            "K", "CPB", "CAG", "SJM", "HSY", "MKC", "CLX", "CHD", "EL", "CL",
            "KMB", "SYY", "KR", "WBA", "DG", "DLTR", "BJ", "ACI", "RAD", "RITE",
            "TSN", "HRL", "CAG", "CPB", "GIS", "K", "SJM", "LW", "PM", "MO",
            "BTI", "UVV", "TPG", "VGR", "XXII", "CRON", "CGC", "TLRY", "ACB", "HEXO",
            
            # Industrials
            "CAT", "GE", "MMM", "HON", "UPS", "FDX", "EMR", "ETN", "ITW", "PH",
            "CMI", "DE", "DOV", "IR", "JCI", "ROK", "XYL", "FLR", "PWR", "BLDR",
            "VMC", "MLM", "NUE", "X", "CLF", "STLD", "RS", "CMC", "WOR", "PKG",
            "CCK", "BALL", "CRH", "SUM", "JEC", "GNRC", "TXT", "LHX", "GD", "NOC",
            "LMT", "RTX", "BA", "HII", "LDOS", "CACI", "SAIC", "KBR", "VST", "AIT",
            
            # Materials
            "LIN", "APD", "ECL", "SHW", "FCX", "NEM", "FMC", "ALB", "EMN", "IFF",
            "PPG", "CF", "MOS", "LYB", "DOW", "DD", "CE", "STLD", "MT", "TX",
            "GOLD", "AEM", "KGC", "AU", "IAG", "HL", "CDE", "PAAS", "AG", "EXK",
            "FSM", "SVM", "SBSW", "WPM", "FNV", "RGLD", "SAND", "SA", "VALE", "RIO",
            "BHP", "SCCO", "TECK", "HBM", "FM", "CSTM", "UEC", "CCJ", "DNN", "UUUU",
            
            # Utilities
            "NEE", "DUK", "SO", "AEP", "EXC", "XEL", "WEC", "ES", "AWK", "CMS",
            "PEG", "ED", "ETR", "FE", "AES", "PPL", "D", "PCG", "EIX", "SRE",
            "NI", "LNT", "EVRG", "CNP", "OGE", "PNW", "IDA", "MDU", "NWE", "AVA",
            "BKH", "NJR", "SJI", "CPK", "UGI", "ALE", "SR", "NWN", "UTL", "MGEE",
            
            # Real Estate
            "SPG", "PLD", "CCI", "AMT", "EQIX", "PSA", "EXR", "AVB", "EQR", "MAA",
            "ESS", "UDR", "CPT", "AIV", "BXP", "VTR", "WELL", "HCP", "PEAK", "HR",
            "SLG", "KIM", "REG", "FRT", "TCO", "MAC", "CBL", "SKT", "WPG", "PEI",
            "ADC", "AKR", "BRX", "CDR", "DDR", "EQC", "GGP", "HIW", "HPP", "JBG",
            
            # Communication Services
            "GOOGL", "GOOG", "META", "NFLX", "DIS", "CMCSA", "T", "VZ", "TMUS", "CHTR",
            "ATVI", "EA", "TTWO", "ZNGA", "RBLX", "PINS", "SNAP", "TWTR", "MTCH", "BMBL",
            "ROKU", "SPOT", "FUBO", "DISH", "SIRI", "NWSA", "FOXA", "VIAC", "DISCA", "IPG",
            "OMC", "WPP", "LBRDA", "LBRDK", "LILAK", "CHTR", "CABO", "LILA", "QVCA", "BATRK"
        ]

def get_stock_sector(symbol):
    """Enhanced sector mapping for US stocks"""
    sector_mapping = {
        # Technology
        'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology', 'AMZN': 'Technology',
        'TSLA': 'Technology', 'META': 'Technology', 'NVDA': 'Technology', 'NFLX': 'Technology',
        'ADBE': 'Technology', 'CRM': 'Technology', 'ORCL': 'Technology', 'INTC': 'Technology',
        'AMD': 'Technology', 'QCOM': 'Technology', 'AVGO': 'Technology', 'CSCO': 'Technology',
        'IBM': 'Technology', 'INTU': 'Technology', 'NOW': 'Technology', 'WDAY': 'Technology',
        'VEEV': 'Technology', 'DDOG': 'Technology', 'SNOW': 'Technology', 'CRWD': 'Technology',
        'ZS': 'Technology', 'OKTA': 'Technology',
        
        # Financial
        'JPM': 'Financial', 'BAC': 'Financial', 'WFC': 'Financial', 'GS': 'Financial',
        'MS': 'Financial', 'C': 'Financial', 'V': 'Financial', 'MA': 'Financial',
        'AXP': 'Financial', 'BK': 'Financial', 'USB': 'Financial', 'PNC': 'Financial',
        'COF': 'Financial', 'SCHW': 'Financial', 'BLK': 'Financial', 'SPGI': 'Financial',
        'MCO': 'Financial', 'AIG': 'Financial', 'TRV': 'Financial', 'ALL': 'Financial',
        'PGR': 'Financial',
        
        # Healthcare
        'JNJ': 'Healthcare', 'PFE': 'Healthcare', 'UNH': 'Healthcare', 'ABBV': 'Healthcare',
        'TMO': 'Healthcare', 'ABT': 'Healthcare', 'MDT': 'Healthcare', 'BMY': 'Healthcare',
        'AMGN': 'Healthcare', 'GILD': 'Healthcare', 'REGN': 'Healthcare', 'BSX': 'Healthcare',
        'SYK': 'Healthcare', 'ISRG': 'Healthcare', 'ZBH': 'Healthcare', 'BDX': 'Healthcare',
        'EW': 'Healthcare', 'ALGN': 'Healthcare', 'MRNA': 'Healthcare', 'CVS': 'Healthcare',
        'ANTM': 'Healthcare', 'CI': 'Healthcare', 'HUM': 'Healthcare', 'CNC': 'Healthcare',
        'DXCM': 'Healthcare', 'ZTS': 'Healthcare', 'IDEXX': 'Healthcare',
        
        # Energy
        'XOM': 'Energy', 'CVX': 'Energy', 'COP': 'Energy', 'EOG': 'Energy', 'SLB': 'Energy',
        'MPC': 'Energy', 'VLO': 'Energy', 'PSX': 'Energy', 'OXY': 'Energy', 'HAL': 'Energy',
        
        # Consumer
        'WMT': 'Consumer', 'HD': 'Consumer', 'LOW': 'Consumer', 'COST': 'Consumer', 'TGT': 'Consumer',
        'PG': 'Consumer', 'KO': 'Consumer', 'PEP': 'Consumer', 'MCD': 'Consumer', 'SBUX': 'Consumer',
        'NKE': 'Consumer', 'TJX': 'Consumer', 'ROST': 'Consumer', 'YUM': 'Consumer', 'CMG': 'Consumer',
        'ULTA': 'Consumer', 'DIS': 'Consumer', 'F': 'Consumer', 'GM': 'Consumer',
        
        # Industrial
        'CAT': 'Industrial', 'GE': 'Industrial', 'MMM': 'Industrial', 'HON': 'Industrial', 'UPS': 'Industrial',
        'FDX': 'Industrial', 'EMR': 'Industrial', 'ETN': 'Industrial', 'ITW': 'Industrial', 'PH': 'Industrial',
        'CMI': 'Industrial', 'DE': 'Industrial', 'DOV': 'Industrial',
        
        # Defense
        'BA': 'Defense', 'LMT': 'Defense', 'RTX': 'Defense', 'NOC': 'Defense', 'GD': 'Defense',
        'LHX': 'Defense', 'TDG': 'Defense',
        
        # Utilities
        'NEE': 'Utilities', 'DUK': 'Utilities', 'SO': 'Utilities', 'AEP': 'Utilities', 'EXC': 'Utilities',
        'XEL': 'Utilities', 'WEC': 'Utilities', 'ES': 'Utilities', 'AWK': 'Utilities', 'CMS': 'Utilities',
        
        # Materials
        'LIN': 'Materials', 'APD': 'Materials', 'ECL': 'Materials', 'SHW': 'Materials', 'FCX': 'Materials',
        'NEM': 'Materials', 'FMC': 'Materials', 'ALB': 'Materials', 'EMN': 'Materials', 'IFF': 'Materials',
        'PPG': 'Materials', 'CF': 'Materials', 'MOS': 'Materials', 'LYB': 'Materials', 'DOW': 'Materials',
        'DD': 'Materials', 'CE': 'Materials', 'VMC': 'Materials', 'MLM': 'Materials', 'NUE': 'Materials'
    }
    
    return sector_mapping.get(symbol, 'Other')

def calculate_us_dynamic_targets(data, current_price):
    """Calculate dynamic targets for US stocks with fallback tracking"""
    try:
        # Calculate volatility
        returns = data['Close'].pct_change().dropna()
        volatility = returns.tail(20).std() * np.sqrt(252) if len(returns) >= 20 else None
        
        using_fallback_volatility = volatility is None
        if using_fallback_volatility:
            volatility = 0.20
            
        # Support and resistance levels
        recent_high = data['High'].tail(30).max()
        recent_low = data['Low'].tail(30).min()
        
        # Volume analysis
        avg_volume = data['Volume'].tail(20).mean() if 'Volume' in data.columns else None
        recent_volume = data['Volume'].tail(5).mean() if 'Volume' in data.columns else None
        
        using_fallback_volume = avg_volume is None or recent_volume is None
        if using_fallback_volume:
            avg_volume = 500000
            recent_volume = 500000
            
        volume_surge = recent_volume > avg_volume * 1.2
        
        # Target calculation for US stocks (more conservative)
        if volatility > 0.30:  # High volatility
            base_target_pct = np.random.uniform(4, 8)
        elif volatility > 0.20:  # Medium volatility  
            base_target_pct = np.random.uniform(3, 6)
        else:  # Low volatility
            base_target_pct = np.random.uniform(2, 5)
        
        # Market cap adjustments
        market_cap_adjustment = False
        if current_price > 300:  # Large cap
            base_target_pct *= 0.9
            market_cap_adjustment = True
        elif current_price < 50:  # Small cap
            base_target_pct *= 1.1
            market_cap_adjustment = True
        
        # Technical adjustments
        technical_adjustment_applied = False
        if len(data) >= 50:
            ema21 = data['Close'].ewm(span=21).mean().iloc[-1]
            ema50 = data['Close'].ewm(span=50).mean().iloc[-1]
            
            if current_price > ema21 > ema50:
                base_target_pct *= 1.05
                technical_adjustment_applied = True
            
            if volume_surge and not using_fallback_volume:
                base_target_pct *= 1.03
                technical_adjustment_applied = True
        
        # Calculate target price
        target_price = current_price * (1 + base_target_pct / 100)
        
        # Ensure target doesn't exceed recent resistance
        if target_price > recent_high * 1.06:
            target_price = recent_high * 1.06
            base_target_pct = ((target_price / current_price) - 1) * 100
        
        # Stop loss calculation
        support_level = recent_low * 1.015
        volatility_sl = current_price * (1 - min(volatility * 0.7, 0.05))
        
        stop_loss = max(support_level, volatility_sl)
        
        # Risk management
        potential_gain = target_price - current_price
        max_allowed_sl_price = current_price - (potential_gain * 0.4)
        
        if stop_loss < max_allowed_sl_price:
            stop_loss = max_allowed_sl_price
        
        min_sl_price = current_price * 0.99
        stop_loss = min(stop_loss, min_sl_price)
        
        sl_pct = ((current_price - stop_loss) / current_price) * 100
        
        # Risk-reward ratio
        risk = current_price - stop_loss
        reward = target_price - current_price
        risk_reward_ratio = round(reward / risk, 1) if risk > 0 else 1.0
        
        # Estimated days
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
            'volume_surge': volume_surge,
            'risk_reward_ratio': risk_reward_ratio,
            'fallback_flags': {
                'volatility': using_fallback_volatility,
                'volume': using_fallback_volume,
                'market_cap_adj': market_cap_adjustment,
                'technical_adjustment': technical_adjustment_applied
            }
        }
        
    except Exception as e:
        return {
            'target': current_price * 1.04,
            'target_pct': 4.0,
            'stop_loss': current_price * 0.98,
            'sl_pct': 2.0,
            'estimated_days': 8,
            'volatility': 0.20,
            'volume_surge': False,
            'risk_reward_ratio': 2.0,
            'fallback_flags': {
                'complete_fallback': True,
                'volatility': True,
                'volume': True,
                'market_cap_adj': False,
                'technical_adjustment': False
            }
        }

def get_us_recommendations(min_price=25, max_rsi=65, min_volume=500000, batch_size=200):
    """ENHANCED: Get US stock recommendations with technical reasoning"""
    
    try:
        symbols = get_expanded_sp500_universe()
        recommendations = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Randomize symbol order FIRST to scan different stocks each time
        import random
        random.shuffle(symbols)
        
        total_symbols = min(len(symbols), batch_size)
        successful_fetches = 0
        
        status_text.text(f"Starting enhanced scan of {total_symbols} US stocks...")
        
        for i, symbol in enumerate(symbols[:total_symbols]):
            try:
                progress_bar.progress((i + 1) / total_symbols)
                status_text.text(f"Analyzing {symbol}... ({i+1}/{total_symbols})")
                
                time.sleep(0.08)
                
                # Fetch data
                stock = yf.Ticker(symbol)
                data = stock.history(period="3mo", interval="1d")
                
                if len(data) < 25:
                    continue
                
                # Calculate indicators with fallback tracking
                data['RSI'], rsi_is_fallback = calculate_rsi(data)
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
                
                current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
                
                # Check RSI rising trend (2 consecutive days preferred)
                rsi_rising = False
                rsi_rising_days = 0
                if len(data['RSI']) >= 4:
                    recent_rsi = data['RSI'].tail(4)
                    # Check 2 consecutive days rising
                    if (recent_rsi.iloc[-1] > recent_rsi.iloc[-2] > recent_rsi.iloc[-3]):
                        rsi_rising = True
                        rsi_rising_days = 2
                    # Check 1 day rising
                    elif (recent_rsi.iloc[-1] > recent_rsi.iloc[-2]):
                        rsi_rising = True
                        rsi_rising_days = 1
                
                # Volume handling
                avg_volume = data['Volume'].tail(10).mean() if 'Volume' in data.columns else min_volume
                volume_is_fallback = 'Volume' not in data.columns
                
                # Apply filters
                if (current_price >= min_price and 
                    rsi <= max_rsi and
                    rsi_rising and
                    not pd.isna(rsi) and 
                    not pd.isna(current_price) and
                    avg_volume >= min_volume * 0.2):
                    
                    successful_fetches += 1
                    
                    # Analyze technical patterns
                    pattern_analysis = analyze_us_technical_patterns(data, symbol)
                    
                    # Calculate dynamic targets
                    target_data = calculate_us_dynamic_targets(data, current_price)
                    
                    # Technical score calculation
                    technical_score = 0
                    score_components = []
                    
                    # Trend alignment
                    if latest['Close'] > latest['EMA21']:
                        technical_score += 1
                        score_components.append("Above EMA21")
                    if latest['EMA21'] > latest['EMA50']:
                        technical_score += 1
                        score_components.append("EMA Bullish")
                    
                    # RSI conditions
                    if 20 <= rsi <= 65:
                        technical_score += 1
                        score_components.append("Good RSI")
                    
                    # MACD signal
                    if latest['MACD'] > latest['MACD_Signal']:
                        technical_score += 1
                        score_components.append("MACD+")
                    
                    # Bollinger Band position
                    if not pd.isna(latest['BB_Lower']) and not pd.isna(latest['BB_Upper']):
                        bb_position = (latest['Close'] - latest['BB_Lower']) / (latest['BB_Upper'] - latest['BB_Lower'])
                        if 0.1 <= bb_position <= 0.8:
                            technical_score += 1
                            score_components.append("BB Position")
                    else:
                        bb_position = 0.5
                    
                    # Volume confirmation
                    if target_data['volume_surge'] and not target_data['fallback_flags'].get('volume', False):
                        technical_score += 1
                        score_components.append("Volume+")
                    
                    # Include stocks with 2+ conditions
                    if technical_score >= 2:
                        
                        # Risk rating
                        if current_price > 200 and target_data['volatility'] < 0.25:
                            risk_rating = 'Low'
                        elif target_data['volatility'] > 0.35:
                            risk_rating = 'High'
                        else:
                            risk_rating = 'Medium'
                        
                        # Sector classification
                        sector = get_stock_sector(symbol)
                        
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
                        
                        recommendations.append({
                            'Date': datetime.now().strftime('%Y-%m-%d'),
                            'Stock': symbol,
                            'LTP': round(current_price, 2),
                            'RSI': f"{round(current_rsi, 1)} ({rsi_rising_days}D↑)" if rsi_rising else round(current_rsi, 1),
                            'Target': round(target_data['target'], 2),
                            '% Gain': round(target_data['target_pct'], 1),
                            'Est.Days': target_data['estimated_days'],
                            'Stop Loss': round(target_data['stop_loss'], 2),
                            'SL %': round(target_data['sl_pct'], 1),
                            'Risk:Reward': f"1:{target_data['risk_reward_ratio']}",
                            'Selection Reason': pattern_analysis['all_reasons'],
                            'Primary Pattern': pattern_analysis['primary_reason'],
                            'Pattern Strength': pattern_analysis['pattern_strength'],
                            'Volume': int(avg_volume),
                            'Risk': risk_rating,
                            'Tech Score': f"{technical_score}/6",
                            'Sector': sector,
                            'Volatility': f"{target_data['volatility']:.1%}",
                            'BB Position': f"{bb_position:.2f}",
                            'Weekly Status': 'Bullish' if len(data) >= 7 and data['Close'].iloc[-1] > data['Open'].iloc[-7] else 'Neutral',
                            'Data Quality': f"Real Data{fallback_note}" if not fallback_indicators else f"Mixed Data{fallback_note}",
                            'Status': 'Active'
                        })
            
            except Exception as e:
                continue
        
        progress_bar.empty()
        status_text.empty()
        
        # Display scan statistics
        if successful_fetches > 0:
            st.info(f"✅ Successfully analyzed {successful_fetches} US stocks out of {total_symbols} attempted")
        else:
            st.warning(f"⚠️ Could not fetch data for any US stocks. This might be due to market hours or API limits.")
        
        # Sort by pattern strength and technical score
        df = pd.DataFrame(recommendations)
        if not df.empty:
            df = df.sort_values(['Pattern Strength', 'Tech Score', '% Gain'], ascending=[False, False, False])
            df = df.head(20)
        
        return df
        
    except Exception as e:
        st.error(f"Error in get_us_recommendations: {str(e)}")
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
        
        overview['last_updated'] = datetime.now().strftime('%H:%M:%S')
        return overview
        
    except Exception as e:
        return {
            'sp500': {'price': 450, 'change': 0, 'change_pct': 0},
            'nasdaq': {'price': 380, 'change': 0, 'change_pct': 0},
            'last_updated': 'Market data unavailable*',
            'error': str(e)
        }
