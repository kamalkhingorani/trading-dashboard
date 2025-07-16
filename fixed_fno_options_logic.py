import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import calendar

def get_next_expiry_dates():
    """Get correct expiry dates for Indian options"""
    today = datetime.now()
    
    # Find next Thursday for Nifty (weekly)
    days_ahead = 3 - today.weekday()  # Thursday is weekday 3
    if days_ahead <= 0:  # Thursday already passed this week
        days_ahead += 7
    next_nifty_expiry = today + timedelta(days=days_ahead)
    
    # Find last Thursday of current month for Bank Nifty (monthly)
    current_month = today.month
    current_year = today.year
    
    # Get last day of current month
    last_day = calendar.monthrange(current_year, current_month)[1]
    last_date = datetime(current_year, current_month, last_day)
    
    # Find last Thursday of the month
    while last_date.weekday() != 3:  # Thursday is weekday 3
        last_date -= timedelta(days=1)
    
    # If last Thursday has passed, get last Thursday of next month
    if last_date <= today:
        if current_month == 12:
            next_month = 1
            next_year = current_year + 1
        else:
            next_month = current_month + 1
            next_year = current_year
            
        last_day = calendar.monthrange(next_year, next_month)[1]
        last_date = datetime(next_year, next_month, last_day)
        
        while last_date.weekday() != 3:  # Thursday is weekday 3
            last_date -= timedelta(days=1)
    
    next_banknifty_expiry = last_date
    
    # Stock options also expire on last Thursday of the month (monthly)
    next_stock_expiry = next_banknifty_expiry
    
    return {
        'nifty': next_nifty_expiry,
        'banknifty': next_banknifty_expiry,
        'stocks': next_stock_expiry
    }

def get_correct_strike_prices(underlying_price, option_type='index', num_strikes=5):
    """Get correct strike prices based on Indian market rules"""
    
    if option_type == 'index':
        if underlying_price >= 20000:  # Nifty/Bank Nifty range
            # Strike interval of 50 for Nifty, 100 for Bank Nifty
            if underlying_price > 40000:  # Bank Nifty range
                interval = 100
            else:  # Nifty range
                interval = 50
        else:
            interval = 25
    else:  # Stock options
        if underlying_price >= 2000:
            interval = 100
        elif underlying_price >= 1000:
            interval = 50
        elif underlying_price >= 500:
            interval = 20
        elif underlying_price >= 250:
            interval = 10
        else:
            interval = 5
    
    # Generate ATM and nearby strikes
    atm_strike = round(underlying_price / interval) * interval
    
    strikes = []
    # For directional recommendations, focus on ATM and slightly OTM strikes
    for i in range(-1, num_strikes):
        strike = atm_strike + (i * interval)
        if strike > 0:
            strikes.append(strike)
    
    return strikes

def fetch_current_index_prices():
    """Fetch current prices of indices with technical indicators"""
    try:
        # Fetch current Nifty price with history
        nifty = yf.Ticker("^NSEI")
        nifty_data = nifty.history(period="1mo")
        if not nifty_data.empty:
            nifty_price = nifty_data['Close'].iloc[-1]
            nifty_sma20 = nifty_data['Close'].tail(20).mean()
            nifty_trend = "BULLISH" if nifty_price > nifty_sma20 else "BEARISH"
        else:
            nifty_price = 22000.0
            nifty_trend = "NEUTRAL"
        
        # Fetch current Bank Nifty price with history
        banknifty = yf.Ticker("^NSEBANK")
        banknifty_data = banknifty.history(period="1mo")
        if not banknifty_data.empty:
            banknifty_price = banknifty_data['Close'].iloc[-1]
            banknifty_sma20 = banknifty_data['Close'].tail(20).mean()
            banknifty_trend = "BULLISH" if banknifty_price > banknifty_sma20 else "BEARISH"
        else:
            banknifty_price = 48000.0
            banknifty_trend = "NEUTRAL"
        
        return {
            'NIFTY': {
                'price': round(nifty_price, 2),
                'trend': nifty_trend
            },
            'BANKNIFTY': {
                'price': round(banknifty_price, 2),
                'trend': banknifty_trend
            }
        }
    except:
        return {
            'NIFTY': {'price': 22000.0, 'trend': 'NEUTRAL'},
            'BANKNIFTY': {'price': 48000.0, 'trend': 'NEUTRAL'}
        }

def fetch_stock_prices(symbols):
    """Fetch current prices of stocks with technical bias"""
    prices = {}
    for symbol in symbols:
        try:
            stock = yf.Ticker(f"{symbol}.NS")
            data = stock.history(period="1mo")
            if not data.empty:
                current_price = round(data['Close'].iloc[-1], 2)
                sma20 = data['Close'].tail(20).mean()
                trend = "BULLISH" if current_price > sma20 else "BEARISH"
                
                # Calculate momentum
                price_5d_ago = data['Close'].iloc[-6] if len(data) >= 6 else current_price
                momentum = (current_price - price_5d_ago) / price_5d_ago
                
                prices[symbol] = {
                    'price': current_price,
                    'trend': trend,
                    'momentum': momentum
                }
                if data.empty:
                    continue  # Skip stock with no data
        except:
            prices[symbol] = {
                'price': 1000,
                'trend': 'NEUTRAL',
                'momentum': 0
            }
    
    return prices

def calculate_option_targets(underlying_price, strike, option_type, expiry_days, underlying_name, trend):
    """Calculate realistic option price targets based on directional bias"""
    
    # Moneyness calculation
    if option_type == 'CE':
        moneyness = underlying_price / strike
        is_itm = underlying_price > strike
    else:  # PE
        moneyness = strike / underlying_price  
        is_itm = underlying_price < strike
    
    # Base premium calculation (simplified Black-Scholes approximation)
    time_value = max(0.1, expiry_days / 365)
    
    # Volatility assumptions based on underlying
    if underlying_name in ['NIFTY', 'BANKNIFTY']:
        implied_vol = 0.15 + (0.1 * abs(1 - moneyness))  # 15-25% IV for indices
    else:
        implied_vol = 0.25 + (0.15 * abs(1 - moneyness))  # 25-40% IV for stocks
    
    # Intrinsic value
    if option_type == 'CE':
        intrinsic = max(0, underlying_price - strike)
    else:
        intrinsic = max(0, strike - underlying_price)
    
    # Time value (simplified)
    time_premium = underlying_price * implied_vol * np.sqrt(time_value) * 0.4
    
    current_premium = intrinsic + time_premium
    current_premium = max(current_premium, 5)  # Minimum premium of 5
    
    # Target calculation based on expected move and trend
    if underlying_name in ['NIFTY', 'BANKNIFTY']:
        if trend == "BULLISH" and option_type == "CE":
            expected_move_pct = np.random.uniform(0.03, 0.08)  # 3-8% bullish move
        elif trend == "BEARISH" and option_type == "PE":
            expected_move_pct = np.random.uniform(0.03, 0.08)  # 3-8% bearish move
        else:
            expected_move_pct = np.random.uniform(0.01, 0.04)  # Smaller move against trend
    else:  # Stocks
        if (trend == "BULLISH" and option_type == "CE") or (trend == "BEARISH" and option_type == "PE"):
            expected_move_pct = np.random.uniform(0.04, 0.10)  # 4-10% directional move
        else:
            expected_move_pct = np.random.uniform(0.02, 0.05)  # Smaller move against trend
    
    # Target multiplier based on moneyness and trend alignment
    if (option_type == 'CE' and trend == 'BULLISH') or (option_type == 'PE' and trend == 'BEARISH'):
        # Trend-aligned options
        if abs(moneyness - 1) < 0.02:  # ATM options
            target_multiplier = 1.8 + np.random.uniform(0, 0.7)  # 1.8x to 2.5x
        elif is_itm:  # ITM options
            target_multiplier = 1.3 + np.random.uniform(0, 0.4)  # 1.3x to 1.7x
        else:  # OTM options
            target_multiplier = 2.2 + np.random.uniform(0, 1.3)  # 2.2x to 3.5x
    else:
        # Against-trend options (lower potential)
        target_multiplier = 1.1 + np.random.uniform(0, 0.3)  # 1.1x to 1.4x
    
    target_premium = current_premium * target_multiplier
    gain_pct = ((target_premium - current_premium) / current_premium) * 100
    
    return {
        'current_premium': round(current_premium, 2),
        'target_premium': round(target_premium, 2),
        'gain_pct': round(gain_pct, 1),
        'moneyness': round(moneyness, 3),
        'is_itm': is_itm,
        'trend_aligned': (option_type == 'CE' and trend == 'BULLISH') or (option_type == 'PE' and trend == 'BEARISH')
    }

def generate_fno_opportunities():
    """Generate realistic F&O opportunities with single directional bias"""
    
    # Get current prices and expiry dates
    expiry_dates = get_next_expiry_dates()
    index_data = fetch_current_index_prices()
    
    # Stock symbols for F&O
    url = "https://archives.nseindia.com/content/fo/fo_mktlots.csv"
    fno_df = pd.read_csv(url)
    fno_stocks = fno_df['SYMBOL'].dropna().unique().tolist()

    # Fetch NSE's official F&O list
    fno_df = pd.read_csv("https://archives.nseindia.com/content/fo/fo_mktlots.csv")
    fno_stocks = fno_df['SYMBOL'].dropna().unique().tolist()
    
    stock_data = fetch_stock_prices(fno_stocks)
    
    recommendations = []
    
    # NIFTY Options (Weekly expiry) - Single direction based on trend
    nifty_price = index_data['NIFTY']['price']
    nifty_trend = index_data['NIFTY']['trend']
    nifty_strikes = get_correct_strike_prices(nifty_price, 'index', num_strikes=3)
    nifty_expiry_days = (expiry_dates['nifty'] - datetime.now()).days
    
    # Choose option type based on trend
    nifty_option_type = 'CE' if nifty_trend == 'BULLISH' else 'PE'
    
    for strike in nifty_strikes:
        option_data = calculate_option_targets(
            nifty_price, strike, nifty_option_type, nifty_expiry_days, 'NIFTY', nifty_trend
        )
        
        # Only include high-probability opportunities
        if option_data['trend_aligned'] and 20 <= option_data['gain_pct'] <= 150:
            
            if nifty_option_type == 'CE':
                strategy = f"Bullish on NIFTY (above {nifty_price:.0f})"
                recommendation = 'BUY CE - Uptrend Play'
            else:
                strategy = f"Bearish on NIFTY (below {nifty_price:.0f})"
                recommendation = 'BUY PE - Downtrend Play'
            
           # Avoid duplicate NIFTY entries
nifty_duplicate = any(
    r['Index/Stock'] == 'NIFTY' and
    r['Strike'] == nifty_strike and
    r['Type'] == nifty_option_type
    for r in recommendations
)

if not nifty_duplicate:
    recommendations.append({
        "Index/Stock": "NIFTY",
        "Strike": nifty_strike,
        "Type": nifty_option_type,
        "Price": nifty_price,
        "Trend": index_data['NIFTY']['trend'],
        "Momentum": index_data['NIFTY']['momentum'],
        "Entry": "AUTO"
    })

    
    # BANK NIFTY Options (Monthly expiry) - Single direction based on trend
    banknifty_price = index_data['BANKNIFTY']['price']
    banknifty_trend = index_data['BANKNIFTY']['trend']
    banknifty_strikes = get_correct_strike_prices(banknifty_price, 'index', num_strikes=3)
    banknifty_expiry_days = (expiry_dates['banknifty'] - datetime.now()).days
    
    # Choose option type based on trend
    banknifty_option_type = 'CE' if banknifty_trend == 'BULLISH' else 'PE'
    
    for strike in banknifty_strikes:
        option_data = calculate_option_targets(
            banknifty_price, strike, banknifty_option_type, banknifty_expiry_days, 'BANKNIFTY', banknifty_trend
        )
        
        if option_data['trend_aligned'] and 20 <= option_data['gain_pct'] <= 150:
            
            if banknifty_option_type == 'CE':
                strategy = f"Banking sector bullish (above {banknifty_price:.0f})"
                recommendation = 'BUY CE - Banking Rally'
            else:
                strategy = f"Banking sector bearish (below {banknifty_price:.0f})"
                recommendation = 'BUY PE - Banking Weakness'
            
            recommendations.append({
                'Index/Stock': 'BANKNIFTY',
                'Current Price': banknifty_price,
                'Strike': int(strike),
                'Type': banknifty_option_type,
                'LTP': option_data['current_premium'],
                'Target': option_data['target_premium'],
                '% Gain': option_data['gain_pct'],
                'Days to Expiry': banknifty_expiry_days,
                'Expiry Date': expiry_dates['banknifty'].strftime('%d-%b-%Y'),
                'Moneyness': 'ATM' if abs(option_data['moneyness'] - 1) < 0.02 else ('ITM' if option_data['is_itm'] else 'OTM'),
                'Strategy': strategy,
                'Recommendation': recommendation,
                'Risk Level': 'High'  # Bank Nifty is more volatile
            })
    
    # Stock Options (Monthly expiry) - Single direction per stock
    stock_expiry_days = (expiry_dates['stocks'] - datetime.now()).days
    
    for stock in fno_stocks[:10]:  # Limit to top 3 stocks for memory
        stock_info = stock_data[stock]
        stock_price = stock_info['price']
        stock_trend = stock_info['trend']
        stock_momentum = stock_info['momentum']
        
        # Determine direction based on trend and momentum
        if stock_trend == 'BULLISH' and stock_momentum > 0.01:
            option_type = 'CE'
            strategy = f"{stock} bullish momentum play"
            recommendation = f'BUY CE - {stock} Upside'
        elif stock_trend == 'BEARISH' and stock_momentum < -0.01:
            option_type = 'PE'
            strategy = f"{stock} bearish breakdown"
            recommendation = f'BUY PE - {stock} Downside'
        else:
            # Skip stocks with unclear direction
            continue
        
        stock_strikes = get_correct_strike_prices(stock_price, 'stock', num_strikes=2)
        
        for strike in stock_strikes:
            option_data = calculate_option_targets(
                stock_price, strike, option_type, stock_expiry_days, stock, stock_trend
            )
            
            if option_data['trend_aligned'] and 25 <= option_data['gain_pct'] <= 120:
                
                recommendations.append({
                    'Index/Stock': stock,
                    'Current Price': stock_price,
                    'Strike': int(strike),
                    'Type': option_type,
                    'LTP': option_data['current_premium'],
                    'Target': option_data['target_premium'],
                    '% Gain': option_data['gain_pct'],
                    'Days to Expiry': stock_expiry_days,
                    'Expiry Date': expiry_dates['stocks'].strftime('%d-%b-%Y'),
                    'Moneyness': 'ATM' if abs(option_data['moneyness'] - 1) < 0.02 else ('ITM' if option_data['is_itm'] else 'OTM'),
                    'Strategy': strategy,
                    'Recommendation': recommendation,
                    'Risk Level': 'High'
                })
    
    # Convert to DataFrame and sort by gain potential
    df = pd.DataFrame(recommendations)
    if not df.empty:
        # Sort by Risk Level (Medium first) and then by % Gain
        df['risk_sort'] = df['Risk Level'].map({'Medium': 0, 'High': 1})
        df = df.sort_values(['risk_sort', '% Gain'], ascending=[True, False])
        df = df.drop('risk_sort', axis=1)
    
    return df

def get_options_summary(df):
    """Get summary statistics for options recommendations"""
    if df.empty:
        return {}
    
    # Count by option type
    ce_count = len(df[df['Type'] == 'CE'])
    pe_count = len(df[df['Type'] == 'PE'])
    
    # Group by underlying
    underlying_counts = df['Index/Stock'].value_counts().to_dict()
    
    return {
        'total_opportunities': len(df),
        'avg_gain_potential': df['% Gain'].mean(),
        'max_gain_potential': df['% Gain'].max(),
        'min_gain_potential': df['% Gain'].min(),
        'ce_count': ce_count,
        'pe_count': pe_count,
        'nifty_options': underlying_counts.get('NIFTY', 0),
        'banknifty_options': underlying_counts.get('BANKNIFTY', 0),
        'stock_options': len(df[~df['Index/Stock'].isin(['NIFTY', 'BANKNIFTY'])]),
        'high_risk_count': len(df[df['Risk Level'] == 'High']),
        'medium_risk_count': len(df[df['Risk Level'] == 'Medium']),
        'bullish_bias': ce_count > pe_count,
        'market_view': 'Bullish' if ce_count > pe_count else 'Bearish' if pe_count > ce_count else 'Neutral'
    }

def validate_option_data(df):
    """Validate that option data follows Indian market rules"""
    errors = []
    
    for _, row in df.iterrows():
        # Check strike intervals
        underlying = row['Index/Stock']
        strike = row['Strike']
        current_price = row['Current Price']
        
        if underlying == 'NIFTY':
            if strike % 50 != 0:
                errors.append(f"NIFTY strike {strike} not in 50-point intervals")
        elif underlying == 'BANKNIFTY':
            if strike % 100 != 0:
                errors.append(f"BANKNIFTY strike {strike} not in 100-point intervals")
        else:  # Stock options
            valid_intervals = [5, 10, 20, 50, 100]
            if not any(strike % interval == 0 for interval in valid_intervals):
                errors.append(f"{underlying} strike {strike} not in valid intervals")
        
        # Check expiry dates
        expiry_str = row['Expiry Date']
        try:
            expiry_date = datetime.strptime(expiry_str, '%d-%b-%Y')
            if expiry_date.weekday() != 3:  # Not Thursday
                errors.append(f"{underlying} expiry {expiry_str} not on Thursday")
        except:
            errors.append(f"Invalid expiry date format: {expiry_str}")
    
    return errors
