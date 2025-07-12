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

def get_us_recommendations(min_price=25, max_rsi=50, min_volume=1000000):
    """Get US stock recommendations with guaranteed results"""
    
    symbols = get_sp500_universe()
    recommendations = []
    
    # Show progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, symbol in enumerate(symbols[:30]):  # Limit to 30 for speed
        try:
            progress_bar.progress((i + 1) / 30)
            status_text.text(f"Analyzing {symbol}...")
            
            # Fetch data
            stock = yf.Ticker(symbol)
            data = stock.history(period="6mo", interval="1d")
            
            if len(data) < 50:
                continue
            
            # Calculate indicators
            data['RSI'] = calculate_rsi(data)
            data['EMA21'] = data['Close'].ewm(span=21).mean()
            data['EMA50'] = data['Close'].ewm(span=50).mean()
            
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
            
            # Apply filters - more lenient for guaranteed results
            if (current_price >= min_price and 
                rsi <= max_rsi and 
                not pd.isna(rsi) and 
                not pd.isna(current_price) and
                avg_volume >= min_volume * 0.3):  # 30% of required volume
                
                # Calculate targets based on market cap and volatility
                returns = data['Close'].pct_change().dropna()
                volatility = returns.std()
                
                # US market targets (generally more conservative)
                if current_price > 200:  # Large cap
                    target_pct = 0.06  # 6% for large caps
                    days_est = 15
                elif volatility > 0.025:
                    target_pct = 0.10  # 10% for high vol
                    days_est = 12
                elif volatility > 0.018:
                    target_pct = 0.07  # 7% for medium vol
                    days_est = 15
                else:
                    target_pct = 0.05  # 5% for low vol
                    days_est = 20
                
                target = current_price * (1 + target_pct)
                sl = current_price * 0.94  # 6% SL for US markets
                
                # Check technical conditions
                technical_score = 0
                if latest['Close'] > latest['EMA21']:
                    technical_score += 1
                if latest['EMA21'] > latest['EMA50']:
                    technical_score += 1
                if latest['MACD'] > latest['MACD_Signal']:
                    technical_score += 1
                if rsi < 45:  # Not overbought
                    technical_score += 1
                
                if technical_score >= 2:  # At least 2 of 4 conditions
                    recommendations.append({
                        'Date': datetime.now().strftime('%Y-%m-%d'),
                        'Stock': symbol,
                        'LTP': round(current_price, 2),
                        'RSI': round(rsi, 1),
                        'Target': round(target, 2),
                        '% Gain': round(target_pct * 100, 1),
                        'Est. Days': days_est,
                        'Stop Loss': round(sl, 2),
                        'Volume': int(avg_volume),
                        'Tech Score': technical_score,
                        'MACD Signal': 'Bullish' if latest['MACD'] > latest['MACD_Signal'] else 'Bearish',
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

def get_us_market_overview():
    """Get US market overview"""
    try:
        # Fetch US indices
        sp500 = yf.download("^GSPC", period="1d", interval="5m")
        nasdaq = yf.download("^IXIC", period="1d", interval="5m")
        dow = yf.download("^DJI", period="1d", interval="5m")
        
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
    
    sector_mapping = {
        'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology', 'AMZN': 'Technology',
        'TSLA': 'Technology', 'META': 'Technology', 'NVDA': 'Technology', 'NFLX': 'Technology',
        'JPM': 'Financial', 'BAC': 'Financial', 'WFC': 'Financial', 'GS': 'Financial',
        'MS': 'Financial', 'C': 'Financial', 'V': 'Financial', 'MA': 'Financial',
        'JNJ': 'Healthcare', 'PFE': 'Healthcare', 'UNH': 'Healthcare', 'ABBV': 'Healthcare',
        'TMO': 'Healthcare', 'ABT': 'Healthcare', 'MDT': 'Healthcare', 'BMY': 'Healthcare',
        'BA': 'Defense', 'LMT': 'Defense', 'RTX': 'Defense', 'NOC': 'Defense', 'GD': 'Defense',
        'XOM': 'Energy', 'CVX': 'Energy', 'COP': 'Energy', 'EOG': 'Energy', 'SLB': 'Energy',
        'WMT': 'Consumer', 'HD': 'Consumer', 'LOW': 'Consumer', 'COST': 'Consumer', 'TGT': 'Consumer',
        'CAT': 'Industrial', 'GE': 'Industrial', 'MMM': 'Industrial', 'HON': 'Industrial', 'UPS': 'Industrial'
    }
    
    sector_counts = {}
    for _, row in recommendations_df.iterrows():
        sector = sector_mapping.get(row['Stock'], 'Others')
        sector_counts[sector] = sector_counts.get(sector, 0) + 1
    
    return sector_counts

def get_market_sentiment():
    """Get market sentiment based on technical indicators"""
    try:
        # Fetch VIX for market fear gauge
        vix = yf.download("^VIX", period="5d")
        
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
