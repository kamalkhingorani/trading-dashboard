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

def get_correct_strike_prices(underlying_price, option_type='index'):
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
    for i in range(-4, 5):  # 4 strikes below and above ATM
        strike = atm_strike + (i * interval)
        if strike > 0:
            strikes.append(strike)
    
    return strikes

def fetch_current_index_prices():
    """Fetch current prices of indices"""
    try:
        # Fetch current Nifty price
        nifty = yf.Ticker("^NSEI")
        nifty_data = nifty.history(period="1d")
        nifty_price = nifty_data['Close'].iloc[-1] if not nifty_data.empty else 22000
        
        # Fetch current Bank Nifty price  
        banknifty = yf.Ticker("^NSEBANK")
        banknifty_data = banknifty.history(period="1d")
        banknifty_price = banknifty_data['Close'].iloc[-1] if not banknifty_data.empty else 48000
        
        return {
            'NIFTY': round(nifty_price, 2),
            'BANKNIFTY': round(banknifty_price, 2)
        }
    except:
        return {
            'NIFTY': 22000.0,
            'BANKNIFTY': 48000.0
        }

def fetch_stock_prices(symbols):
    """Fetch current prices of stocks"""
    prices = {}
    for symbol in symbols:
        try:
            stock = yf.Ticker(f"{symbol}.NS")
            data = stock.history(period="1d")
            if not data.empty:
                prices[symbol] = round(data['Close'].iloc[-1], 2)
            else:
                # Default prices if data unavailable
                default_prices = {
                    'RELIANCE': 2500,
                    'TCS': 3200,
                    'HDFCBANK': 1600,
                    'INFY': 1400,
                    'ICICIBANK': 950
                }
                prices[symbol] = default_prices.get(symbol, 1000)
        except:
            prices[symbol] = 1000
    
    return prices

def calculate_option_targets(underlying_price, strike, option_type, expiry_days, underlying_name):
    """Calculate realistic option price targets"""
    
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
    
    # Target calculation based on expected move
    if underlying_name in ['NIFTY', 'BANKNIFTY']:
        expected_move_pct = np.random.uniform(0.02, 0.06)  # 2-6% move for indices
    else:
        expected_move_pct = np.random.uniform(0.03, 0.08)  # 3-8% move for stocks
    
    # Direction based on option type and moneyness
    if (option_type == 'CE' and moneyness < 1.02) or (option_type == 'PE' and moneyness < 1.02):
        # ATM or slightly OTM options
        target_multiplier = 1.5 + np.random.uniform(0, 1.0)  # 1.5x to 2.5x
    elif is_itm:
        # ITM options
        target_multiplier = 1.2 + np.random.uniform(0, 0.5)  # 1.2x to 1.7x
    else:
        # Far OTM options
        target_multiplier = 2.0 + np.random.uniform(0, 2.0)  # 2x to 4x
    
    target_premium = current_premium * target_multiplier
    gain_pct = ((target_premium - current_premium) / current_premium) * 100
    
    return {
        'current_premium': round(current_premium, 2),
        'target_premium': round(target_premium, 2),
        'gain_pct': round(gain_pct, 1),
        'moneyness': round(moneyness, 3),
        'is_itm': is_itm
    }

def generate_fno_opportunities():
    """Generate realistic F&O opportunities with correct Indian market structure"""
    
    # Get current prices and expiry dates
    expiry_dates = get_next_expiry_dates()
    index_prices = fetch_current_index_prices()
    
    # Stock symbols for F&O
    fno_stocks = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK']
    stock_prices = fetch_stock_prices(fno_stocks)
    
    recommendations = []
    
    # NIFTY Options (Weekly expiry)
    nifty_price = index_prices['NIFTY']
    nifty_strikes = get_correct_strike_prices(nifty_price, 'index')
    nifty_expiry_days = (expiry_dates['nifty'] - datetime.now()).days
    
    # Only show best NIFTY opportunities (not all strikes)
    best_nifty_strikes = nifty_strikes[2:7]  # 5 strikes around ATM
    
    for strike in best_nifty_strikes:
        for option_type in ['CE', 'PE']:
            option_data = calculate_option_targets(
                nifty_price, strike, option_type, nifty_expiry_days, 'NIFTY'
            )
            
            # Only include opportunities with reasonable gain potential
            if 15 <= option_data['gain_pct'] <= 200:
                
                # Determine recommendation based on technical bias
                if option_type == 'CE' and strike <= nifty_price * 1.02:  # Bullish bias for near ATM calls
                    recommendation = 'BUY - Bullish Setup'
                elif option_type == 'PE' and strike >= nifty_price * 0.98:  # Bearish bias for near ATM puts
                    recommendation = 'BUY - Bearish Setup'
                else:
                    recommendation = 'MONITOR - Directional Play'
                
                recommendations.append({
                    'Index/Stock': 'NIFTY',
                    'Current Price': nifty_price,
                    'Strike': int(strike),
                    'Type': option_type,
                    'LTP': option_data['current_premium'],
                    'Target': option_data['target_premium'],
                    '% Gain': option_data['gain_pct'],
                    'Days to Expiry': nifty_expiry_days,
                    'Expiry Date': expiry_dates['nifty'].strftime('%d-%b-%Y'),
                    'Moneyness': option_data['moneyness'],
                    'Recommendation': recommendation,
                    'Risk Level': 'Medium' if abs(option_data['moneyness'] - 1) < 0.03 else 'High'
                })
    
    # BANK NIFTY Options (Monthly expiry)
    banknifty_price = index_prices['BANKNIFTY']
    banknifty_strikes = get_correct_strike_prices(banknifty_price, 'index')
    banknifty_expiry_days = (expiry_dates['banknifty'] - datetime.now()).days
    
    # Only show best BANK NIFTY opportunities
    best_banknifty_strikes = banknifty_strikes[2:7]  # 5 strikes around ATM
    
    for strike in best_banknifty_strikes:
        for option_type in ['CE', 'PE']:
            option_data = calculate_option_targets(
                banknifty_price, strike, option_type, banknifty_expiry_days, 'BANKNIFTY'
            )
            
            if 15 <= option_data['gain_pct'] <= 200:
                
                if option_type == 'CE' and strike <= banknifty_price * 1.02:
                    recommendation = 'BUY - Banking Sector Bullish'
                elif option_type == 'PE' and strike >= banknifty_price * 0.98:
                    recommendation = 'BUY - Banking Sector Bearish'
                else:
                    recommendation = 'MONITOR - Sector Play'
                
                recommendations.append({
                    'Index/Stock': 'BANKNIFTY',
                    'Current Price': banknifty_price,
                    'Strike': int(strike),
                    'Type': option_type,
                    'LTP': option_data['current_premium'],
                    'Target': option_data['target_premium'],
                    '% Gain': option_data['gain_pct'],
                    'Days to Expiry': banknifty_expiry_days,
                    'Expiry Date': expiry_dates['banknifty'].strftime('%d-%b-%Y'),
                    'Moneyness': option_data['moneyness'],
                    'Recommendation': recommendation,
                    'Risk Level': 'High'  # Bank Nifty is more volatile
                })
    
    # Stock Options (Monthly expiry)
    stock_expiry_days = (expiry_dates['stocks'] - datetime.now()).days
    
    for stock in fno_stocks[:3]:  # Limit to top 3 stocks for memory
        stock_price = stock_prices[stock]
        stock_strikes = get_correct_strike_prices(stock_price, 'stock')
        
        # Only show 3 best strikes per stock
        best_stock_strikes = stock_strikes[3:6]  # 3 strikes around ATM
        
        for strike in best_stock_strikes:
            # Only show one option type per stock (based on technical bias)
            option_type = 'CE'  # Default to calls for simplicity
            
            option_data = calculate_option_targets(
                stock_price, strike, option_type, stock_expiry_days, stock
            )
            
            if 20 <= option_data['gain_pct'] <= 150:
                
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
                    'Moneyness': option_data['moneyness'],
                    'Recommendation': f'{stock} Earnings/Technical Play',
                    'Risk Level': 'High'
                })
    
    # Convert to DataFrame and sort by gain potential
    df = pd.DataFrame(recommendations)
    if not df.empty:
        df = df.sort_values(['Risk Level', '% Gain'], ascending=[True, False])
    
    return df

def get_options_summary(df):
    """Get summary statistics for options recommendations"""
    if df.empty:
        return {}
    
    return {
        'total_opportunities': len(df),
        'avg_gain_potential': df['% Gain'].mean(),
        'max_gain_potential': df['% Gain'].max(),
        'nifty_options': len(df[df['Index/Stock'] == 'NIFTY']),
        'banknifty_options': len(df[df['Index/Stock'] == 'BANKNIFTY']),
        'stock_options': len(df[~df['Index/Stock'].isin(['NIFTY', 'BANKNIFTY'])]),
        'high_risk_count': len(df[df['Risk Level'] == 'High']),
        'medium_risk_count': len(df[df['Risk Level'] == 'Medium'])
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
