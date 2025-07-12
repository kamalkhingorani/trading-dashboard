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

def calculate_dynamic_targets(data, current_price, market='US'):
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
    avg_volume = data['Volume'].tail(20).mean() if 'Volume' in data.columns else 1000000
    recent_volume = data['Volume'].iloc[-1] if 'Volume' in data.columns else avg_volume
    volume_surge = recent_volume > (avg_volume * 1.2)
    
    # Trend strength
    price_above_sma20 = current_price > sma20
    sma20_above_sma50 = sma20 > sma50
    uptrend = price_above_sma20 and sma20_above_sma50
    
    # US market specific adjustments (more efficient markets, tighter ranges)
    if current_price > 200:  # Large cap stocks
        base_range = (0.02, 0.06)  # 2-6% for large caps
        days_range = (10, 20)
    elif current_price > 50:  # Mid cap stocks
        base_range = (0.03, 0.08)  # 3-8% for mid caps
        days_range = (12, 25)
    else:  # Small cap stocks
        base_range = (0.04, 0.10)  # 4-10% for small caps
        days_range = (15, 30)
    
    # Volatility-based adjustments with randomness
    random_vol_factor = np.random.uniform(0.9, 1.1)
    if volatility > 0.35:  # High volatility
        base_target_pct = np.random.uniform(base_range[1]*0.7, base_range[1]) * random_vol_factor
        days_adjust = np.random.randint(-2, 3)
        days_range = (days_range[0] + days_adjust, days_range[0] + days_adjust + 8)
    elif volatility > 0.25:  # Medium volatility
        base_target_pct = np.random.uniform(base_range[0]*1.5, base_range[1]*0.8) * random_vol_factor
        days_adjust = np.random.randint(0, 3)
        days_range = (days_range[0] + days_adjust, days_range[1])
    else:  # Low volatility
        base_target_pct = np.random.uniform(base_range[0], base_range[0]*2.5) * random_vol_factor
        days_adjust = np.random.randint(2, 5)
        days_range = (days_range[0] + days_adjust, days_range[1] + days_adjust)
    
    # Technical factor adjustments with some randomness
    tech_factor = 1.0
    if uptrend:
        tech_factor *= np.random.uniform(1.1, 1.2)  # 10-20% boost
        days_range = (days_range[0]-1, days_range[1]-2)
    
    if volume_surge:
        tech_factor *= np.random.uniform(1.05, 1.1)  # 5-10% boost
    
    # Recent momentum
    momentum_5d = (current_price - data['Close'].iloc[-6]) / data['Close'].iloc[-6]
    if momentum_5d > 0.02:  # Positive momentum
        tech_factor *= np.random.uniform(1.02, 1.08)
    elif momentum_5d < -0.02:  # Negative momentum
        tech_factor *= np.random.uniform(0.92, 0.98)
    
    base_target_pct *= tech_factor
    
    # Resistance-based ceiling
    resistance_room = (resistance - current_price) / current_price
    if resistance_room < base_target_pct:
        base_target_pct = resistance_room * 0.85  # Leave room before resistance
    
    # Final target with bounds
    final_target_pct = max(base_target_pct, 0.015)  # Minimum 1.5%
    final_target_pct = min(final_target_pct, 0.12)   # Maximum 12%
    
    target_price = current_price * (1 + final_target_pct)
    estimated_days = np.random.randint(days_range[0], days_range[1])
    
    # CORRECTED STOP LOSS CALCULATION
    # Calculate multiple stop loss options
    support_based_sl = (current_price - support) / current_price
    volatility_based_sl = volatility * 0.12  # 12% of annual volatility for US
    atr_based_sl = returns.tail(14).std() * 1.5  # 1.5x ATR
    
    # Risk management rule: Stop loss should be maximum 50% of target gain
    max_allowed_sl_pct = final_target_pct * 0.5  # 50% of potential gain
    
    # Choose the most appropriate stop loss
    sl_pct = min(
        support_based_sl * 0.75,  # 75% of distance to support
        volatility_based_sl,
        atr_based_sl,
        max_allowed_sl_pct,       # Never exceed 50% of gain
        0.06                      # Maximum 6% stop loss for US
    )
    
    # Ensure minimum stop loss (not too tight)
    sl_pct = max(sl_pct, 0.015)  # Minimum 1.5% stop loss for US
    
    # Add some market-specific randomness
    sl_pct *= np.random.uniform(0.95, 1.05)
    
    stop_loss = current_price * (1 - sl_pct)
    
    # Calculate actual risk-reward ratio
    potential_gain = target_price - current_price
    potential_loss = current_price - stop_loss
    risk_reward_ratio = potential_gain / potential_loss if potential_loss > 0 else 999
    
    return {
        'target': target_price,
        'target_pct': final_target_pct * 100,
        'stop_loss': stop_loss,
        'sl_pct': sl_pct * 100,
        'estimated_days': estimated_days,
        'volatility': volatility,
        'volume_surge': volume_surge,
        'risk_reward_ratio': round(risk_reward_ratio, 2),
        'uptrend': uptrend,
        'momentum_5d': momentum_5d
    }

def get_sp500_universe():
    """Get comprehensive S&P 500 stock universe"""
    return [
        # Technology Giants
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "ADBE",
        "CRM", "ORCL", "INTC", "AMD", "QCOM", "AVGO", "CSCO", "IBM", "INTU",
        "NOW", "WDAY", "VEEV", "DDOG", "SNOW", "CRWD", "ZS", "OKTA", "SPLK",
        
        # Financial Services
        "JPM", "BAC", "WFC", "GS", "MS", "C", "AXP", "V", "MA", "PYPL",
        "BK", "USB", "PNC", "COF", "SCHW", "BLK", "SPGI", "MCO", "AIG", "TRV",
        
        # Healthcare & Pharmaceuticals
        "JNJ", "PFE", "UNH", "ABBV", "TMO", "ABT", "MDT", "BMY", "AMGN", "GILD",
        "REGN", "BSX", "SYK", "ISRG", "ZBH", "BDX", "EW", "ALGN", "MRNA", "BNTX",
        
        # Defense & Aerospace
        "BA", "LMT", "RTX", "NOC", "GD", "LHX", "LDOS", "HII", "TDG", "CW",
        
        # Manufacturing & Industrial
        "CAT", "GE", "MMM", "HON", "UPS", "FDX", "EMR", "ETN", "ITW", "PH",
        "CMI", "DE", "DOV", "ROK", "CARR", "OTIS", "PCAR", "WAB", "CHRW",
        
        # Energy & Utilities
        "XOM", "CVX", "COP", "EOG", "SLB", "MPC", "VLO", "PSX", "OXY", "HAL",
        "NEE", "DUK", "SO", "AEP", "EXC", "XEL", "WEC", "ES", "AWK", "CMS",
        
        # Consumer & Retail
        "WMT", "HD", "LOW", "COST", "TGT", "PG", "KO", "PEP", "MCD", "SBUX",
        "NKE", "TJX", "ROST", "YUM", "CMG", "ULTA", "ETSY", "EBAY", "DIS", "F",
        
        # Materials & Chemicals
        "LIN", "APD", "ECL", "SHW", "FCX", "NEM", "FMC", "ALB", "EMN", "IFF",
        "PPG", "CF", "MOS", "LYB", "DOW", "DD", "CE", "VMC", "MLM", "NUE",
        
        # Communication Services
        "VZ", "T", "TMUS", "CMCSA", "CHTR", "FOXA", "FOX", "NWSA", "PARA",
        
        # Transportation
        "DAL", "UAL", "AAL", "LUV", "NSC", "CSX", "UNP", "EXPD", "JBHT",
        
        # Real Estate & REITs
        "AMT", "PLD", "EQIX", "SPG", "O", "PSA", "EQR", "AVB", "ARE", "DLR"
    ]

def get_us_recommendations(min_price=25, max_rsi=60, min_volume=1000000, batch_size=30):
    """Get US stock recommendations with dynamic targets"""
    
    symbols = get_sp500_universe()
    recommendations = []
    
    # Show progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Batch processing for memory management
    total_symbols = min(len(symbols), batch_size)
    
    for i, symbol in enumerate(symbols[:total_symbols]):
        try:
            progress_bar.progress((i + 1) / total_symbols)
            status_text.text(f"Analyzing {symbol}... ({i+1}/{total_symbols})")
            
            # Fetch data
            stock = yf.Ticker(symbol)
            data = stock.history(period="6mo", interval="1d")
            
            if len(data) < 50:
                continue
            
            # Calculate indicators
            data['RSI'] = calculate_rsi(data)
            data['EMA21'] = data['Close'].ewm(span=21).mean()
            data['EMA50'] = data['Close'].ewm(span=50).mean()
            data['SMA20'] = data['Close'].rolling(20).mean()
            
            # MACD
            exp1 = data['Close'].ewm(span=12).mean()
            exp2 = data['Close'].ewm(span=26).mean()
            data['MACD'] = exp1 - exp2
            data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
            
            # Bollinger Bands
            data['BB_Middle'] = data['Close'].rolling(20).mean()
            bb_std = data['Close'].rolling(20).std()
            data['BB_Upper'] = data['BB_Middle'] + (bb_std * 2)
            data['BB_Lower'] = data['BB_Middle'] - (bb_std * 2)
            
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
                avg_volume >= min_volume * 0.3):
                
                # Calculate dynamic targets
                target_data = calculate_dynamic_targets(data, current_price, 'US')
                
                # Only include stocks with good risk-reward ratio
                if target_data['risk_reward_ratio'] >= 2.0:
                    
                    # Technical score calculation (more stringent for US)
                    technical_score = 0
                    
                    # Trend alignment
                    if latest['Close'] > latest['EMA21']:
                        technical_score += 1
                    if latest['EMA21'] > latest['EMA50']:
                        technical_score += 1
                    
                    # RSI conditions (US markets prefer different ranges)
                    if 25 <= rsi <= 55:  # Good RSI range for US stocks
                        technical_score += 1
                    
                    # MACD bullish signal
                    if latest['MACD'] > latest['MACD_Signal']:
                        technical_score += 1
                    
                    # Bollinger Band position (near lower band is good for entry)
                    bb_position = (latest['Close'] - latest['BB_Lower']) / (latest['BB_Upper'] - latest['BB_Lower'])
                    if 0.2 <= bb_position <= 0.6:  # Not at extremes
                        technical_score += 1
                    
                    # Volume confirmation
                    if target_data['volume_surge']:
                        technical_score += 1
                    
                    # Only include stocks with strong technical score (higher bar for US)
                    if technical_score >= 4:  # At least 4 of 6 conditions
                        
                        # Risk rating based on volatility and market cap
                        if current_price > 200 and target_data['volatility'] < 0.25:
                            risk_rating = 'Low'
                        elif target_data['volatility'] > 0.35:
                            risk_rating = 'High'
                        else:
                            risk_rating = 'Medium'
                        
                        # Sector classification
                        sector = get_stock_sector(symbol)
                        
                        # Market cap classification
                        if current_price > 200:
                            market_cap = 'Large Cap'
                        elif current_price > 50:
                            market_cap = 'Mid Cap'
                        else:
                            market_cap = 'Small Cap'
                        
                        recommendations.append({
                            'Date': datetime.now().strftime('%Y-%m-%d'),
                            'Stock': symbol,
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
                            'Tech Score': f"{technical_score}/6",
                            'Sector': sector,
                            'Market Cap': market_cap,
                            'Volatility': f"{target_data['volatility']:.1%}",
                            'BB Position': f"{bb_position:.2f}",
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
    """Get sector for US stock symbol"""
    sector_mapping = {
        # Technology
        'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology', 'AMZN': 'Technology',
        'TSLA': 'Technology', 'META': 'Technology', 'NVDA': 'Technology', 'NFLX': 'Technology',
        'ADBE': 'Technology', 'CRM': 'Technology', 'ORCL': 'Technology', 'INTC': 'Technology',
        'AMD': 'Technology', 'QCOM': 'Technology', 'AVGO': 'Technology', 'CSCO': 'Technology',
        'IBM': 'Technology', 'INTU': 'Technology', 'NOW': 'Technology', 'WDAY': 'Technology',
        'VEEV': 'Technology', 'DDOG': 'Technology', 'SNOW': 'Technology', 'CRWD': 'Technology',
        
        # Financial
        'JPM': 'Financial', 'BAC': 'Financial', 'WFC': 'Financial', 'GS': 'Financial',
        'MS': 'Financial', 'C': 'Financial', 'V': 'Financial', 'MA': 'Financial',
        'AXP': 'Financial', 'PYPL': 'Financial', 'BK': 'Financial', 'USB': 'Financial',
        'PNC': 'Financial', 'COF': 'Financial', 'SCHW': 'Financial', 'BLK': 'Financial',
        'SPGI': 'Financial', 'MCO': 'Financial', 'AIG': 'Financial', 'TRV': 'Financial',
        
        # Healthcare
        'JNJ': 'Healthcare', 'PFE': 'Healthcare', 'UNH': 'Healthcare', 'ABBV': 'Healthcare',
        'TMO': 'Healthcare', 'ABT': 'Healthcare', 'MDT': 'Healthcare', 'BMY': 'Healthcare',
        'AMGN': 'Healthcare', 'GILD': 'Healthcare', 'REGN': 'Healthcare', 'BSX': 'Healthcare',
        'SYK': 'Healthcare', 'ISRG': 'Healthcare', 'ZBH': 'Healthcare', 'BDX': 'Healthcare',
        'EW': 'Healthcare', 'ALGN': 'Healthcare', 'MRNA': 'Healthcare', 'BNTX': 'Healthcare',
        
        # Defense
        'BA': 'Defense', 'LMT': 'Defense', 'RTX': 'Defense', 'NOC': 'Defense', 'GD': 'Defense',
        'LHX': 'Defense', 'LDOS': 'Defense', 'HII': 'Defense', 'TDG': 'Defense', 'CW': 'Defense',
        
        # Industrial
        'CAT': 'Industrial', 'GE': 'Industrial', 'MMM': 'Industrial', 'HON': 'Industrial',
        'UPS': 'Industrial', 'FDX': 'Industrial', 'EMR': 'Industrial', 'ETN': 'Industrial',
        'ITW': 'Industrial', 'PH': 'Industrial', 'CMI': 'Industrial', 'DE': 'Industrial',
        'DOV': 'Industrial', 'ROK': 'Industrial', 'CARR': 'Industrial', 'OTIS': 'Industrial',
        
        # Energy
        'XOM': 'Energy', 'CVX': 'Energy', 'COP': 'Energy', 'EOG': 'Energy', 'SLB': 'Energy',
        'MPC': 'Energy', 'VLO': 'Energy', 'PSX': 'Energy', 'OXY': 'Energy', 'HAL': 'Energy',
        
        # Utilities
        'NEE': 'Utilities', 'DUK': 'Utilities', 'SO': 'Utilities', 'AEP': 'Utilities',
        'EXC': 'Utilities', 'XEL': 'Utilities', 'WEC': 'Utilities', 'ES': 'Utilities',
        'AWK': 'Utilities', 'CMS': 'Utilities',
        
        # Consumer
        'WMT': 'Consumer', 'HD': 'Consumer', 'LOW': 'Consumer', 'COST': 'Consumer',
        'TGT': 'Consumer', 'PG': 'Consumer', 'KO': 'Consumer', 'PEP': 'Consumer',
        'MCD': 'Consumer', 'SBUX': 'Consumer', 'NKE': 'Consumer', 'TJX': 'Consumer',
        'ROST': 'Consumer', 'YUM': 'Consumer', 'CMG': 'Consumer', 'ULTA': 'Consumer',
        'ETSY': 'Consumer', 'EBAY': 'Consumer', 'DIS': 'Consumer', 'F': 'Consumer',
        
        # Materials
        'LIN': 'Materials', 'APD': 'Materials', 'ECL': 'Materials', 'SHW': 'Materials',
        'FCX': 'Materials', 'NEM': 'Materials', 'FMC': 'Materials', 'ALB': 'Materials',
        'EMN': 'Materials', 'IFF': 'Materials', 'PPG': 'Materials', 'CF': 'Materials',
        'MOS': 'Materials', 'LYB': 'Materials', 'DOW': 'Materials', 'DD': 'Materials',
        
        # Communication
        'VZ': 'Communication', 'T': 'Communication', 'TMUS': 'Communication', 'CMCSA': 'Communication',
        'CHTR': 'Communication', 'FOXA': 'Communication', 'FOX': 'Communication', 'NWSA': 'Communication',
        
        # Transportation
        'DAL': 'Transportation', 'UAL': 'Transportation', 'AAL': 'Transportation', 'LUV': 'Transportation',
        'NSC': 'Transportation', 'CSX': 'Transportation', 'UNP': 'Transportation', 'EXPD': 'Transportation',
        'JBHT': 'Transportation',
        
        # Real Estate
        'AMT': 'Real Estate', 'PLD': 'Real Estate', 'EQIX': 'Real Estate', 'SPG': 'Real Estate',
        'O': 'Real Estate', 'PSA': 'Real Estate', 'EQR': 'Real Estate', 'AVB': 'Real Estate',
        'ARE': 'Real Estate', 'DLR': 'Real Estate'
    }
    return sector_mapping.get(symbol, 'Others')

def get_us_market_overview():
    """Get US market overview"""
    try:
        # Fetch US indices
        sp500 = yf.download("^GSPC", period="1d", interval="5m", progress=False)
        nasdaq = yf.download("^IXIC", period="1d", interval="5m", progress=False)
        dow = yf.download("^DJI", period="1d", interval="5m", progress=False)
        
        overview = {}
        
        if not sp500.empty:
            sp500_close = sp500['Close'].iloc[-1]
            sp500_open = sp500['Open'].iloc[0]
            sp500_change = sp500_close - sp500_open
            sp500_pct = (sp500_change / sp500_open) * 100
            
            overview['sp500'] = {
                'price': round(sp500_close, 2),
                'change': round(sp500_change, 2),
                'change_pct': round(sp500_pct, 2)
            }
        
        if not nasdaq.empty:
            nasdaq_close = nasdaq['Close'].iloc[-1]
            nasdaq_open = nasdaq['Open'].iloc[0]
            nasdaq_change = nasdaq_close - nasdaq_open
            nasdaq_pct = (nasdaq_change / nasdaq_open) * 100
            
            overview['nasdaq'] = {
                'price': round(nasdaq_close, 2),
                'change': round(nasdaq_change, 2),
                'change_pct': round(nasdaq_pct, 2)
            }
        
        if not dow.empty:
            dow_close = dow['Close'].iloc[-1]
            dow_open = dow['Open'].iloc[0]
            dow_change = dow_close - dow_open
            dow_pct = (dow_change / dow_open) * 100
            
            overview['dow'] = {
                'price': round(dow_close, 2),
                'change': round(dow_change, 2),
                'change_pct': round(dow_pct, 2)
            }
        
        overview['last_updated'] = datetime.now().strftime('%H:%M:%S')
        return overview
        
    except Exception as e:
        return {
            'sp500': {'price': 0, 'change': 0, 'change_pct': 0},
            'nasdaq': {'price': 0, 'change': 0, 'change_pct': 0},
            'dow': {'price': 0, 'change': 0, 'change_pct': 0},
            'last_updated': 'Error loading data'
        }

def get_sector_analysis_us(recommendations_df):
    """Analyze sector distribution of US recommendations"""
    if recommendations_df.empty:
        return {}
    
    sector_counts = recommendations_df['Sector'].value_counts().to_dict()
    return sector_counts

def get_market_sentiment():
    """Get market sentiment based on VIX and technical indicators"""
    try:
        # Fetch VIX for market fear gauge
        vix = yf.download("^VIX", period="5d", progress=False)
        
        if not vix.empty:
            current_vix = vix['Close'].iloc[-1]
            
            if current_vix < 15:
                sentiment = "Very Bullish (Low Fear)"
            elif current_vix < 20:
                sentiment = "Bullish (Moderate Fear)"
            elif current_vix < 30:
                sentiment = "Neutral (Normal Fear)"
            elif current_vix < 40:
                sentiment = "Bearish (High Fear)"
            else:
                sentiment = "Very Bearish (Extreme Fear)"
                
            return {
                'vix': round(current_vix, 2),
                'sentiment': sentiment,
                'last_updated': datetime.now().strftime('%H:%M:%S')
            }
        else:
            return {'vix': 20, 'sentiment': 'Neutral', 'last_updated': 'Data unavailable'}
            
    except Exception:
        return {'vix': 20, 'sentiment': 'Neutral', 'last_updated': 'Error loading data'}
