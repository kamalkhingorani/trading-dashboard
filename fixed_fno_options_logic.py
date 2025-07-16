import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import calendar

def get_next_expiry_dates():
    today = datetime.now()
    days_ahead = 3 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_nifty_expiry = today + timedelta(days=days_ahead)

    current_month = today.month
    current_year = today.year
    last_day = calendar.monthrange(current_year, current_month)[1]
    last_date = datetime(current_year, current_month, last_day)
    while last_date.weekday() != 3:
        last_date -= timedelta(days=1)

    if last_date <= today:
        next_month = 1 if current_month == 12 else current_month + 1
        next_year = current_year + 1 if current_month == 12 else current_year
        last_day = calendar.monthrange(next_year, next_month)[1]
        last_date = datetime(next_year, next_month, last_day)
        while last_date.weekday() != 3:
            last_date -= timedelta(days=1)

    return {
        'nifty': next_nifty_expiry,
        'banknifty': last_date,
        'stocks': last_date
    }

def get_correct_strike_prices(price, option_type='index', num_strikes=5):
    if option_type == 'index':
        interval = 100 if price > 40000 else 50 if price >= 20000 else 25
    else:
        if price >= 2000: interval = 100
        elif price >= 1000: interval = 50
        elif price >= 500: interval = 20
        elif price >= 250: interval = 10
        else: interval = 5

    atm = round(price / interval) * interval
    return [atm + (i * interval) for i in range(-1, num_strikes) if atm + (i * interval) > 0]

def fetch_current_index_prices():
    try:
        n_data = yf.Ticker("^NSEI").history(period="1mo")
        b_data = yf.Ticker("^NSEBANK").history(period="1mo")

        n_price = n_data['Close'].iloc[-1] if not n_data.empty else 22000
        b_price = b_data['Close'].iloc[-1] if not b_data.empty else 48000

        n_trend = 'BULLISH' if n_price > n_data['Close'].tail(20).mean() else 'BEARISH'
        b_trend = 'BULLISH' if b_price > b_data['Close'].tail(20).mean() else 'BEARISH'

        return {
            'NIFTY': {'price': round(n_price, 2), 'trend': n_trend},
            'BANKNIFTY': {'price': round(b_price, 2), 'trend': b_trend}
        }
    except:
        return {
            'NIFTY': {'price': 22000.0, 'trend': 'NEUTRAL'},
            'BANKNIFTY': {'price': 48000.0, 'trend': 'NEUTRAL'}
        }

def fetch_stock_prices(symbols):
    prices = {}
    for sym in symbols:
        try:
            data = yf.Ticker(f"{sym}.NS").history(period="1mo")
            if not data.empty:
                cp = round(data['Close'].iloc[-1], 2)
                sma = data['Close'].tail(20).mean()
                trend = 'BULLISH' if cp > sma else 'BEARISH'
                past = data['Close'].iloc[-6] if len(data) >= 6 else cp
                momentum = (cp - past) / past
                prices[sym] = {'price': cp, 'trend': trend, 'momentum': momentum}
        except:
            prices[sym] = {'price': 1000, 'trend': 'NEUTRAL', 'momentum': 0}
    return prices

def calculate_option_targets(price, strike, opt_type, expiry_days, name, trend):
    moneyness = price / strike if opt_type == 'CE' else strike / price
    is_itm = price > strike if opt_type == 'CE' else price < strike
    time_val = max(0.1, expiry_days / 365)
    iv = 0.15 + 0.1 * abs(1 - moneyness) if name in ['NIFTY', 'BANKNIFTY'] else 0.25 + 0.15 * abs(1 - moneyness)
    intrinsic = max(0, price - strike) if opt_type == 'CE' else max(0, strike - price)
    premium = intrinsic + price * iv * np.sqrt(time_val) * 0.4
    premium = max(premium, 5)
    
    if name in ['NIFTY', 'BANKNIFTY']:
        if trend == 'BULLISH' and opt_type == 'CE' or trend == 'BEARISH' and opt_type == 'PE':
            move = np.random.uniform(0.03, 0.08)
        else:
            move = np.random.uniform(0.01, 0.04)
    else:
        if (trend == 'BULLISH' and opt_type == 'CE') or (trend == 'BEARISH' and opt_type == 'PE'):
            move = np.random.uniform(0.04, 0.10)
        else:
            move = np.random.uniform(0.02, 0.05)

    if (opt_type == 'CE' and trend == 'BULLISH') or (opt_type == 'PE' and trend == 'BEARISH'):
        mult = 1.8 + np.random.uniform(0, 0.7) if abs(moneyness - 1) < 0.02 else 1.3 + np.random.uniform(0, 0.4) if is_itm else 2.2 + np.random.uniform(0, 1.3)
    else:
        mult = 1.1 + np.random.uniform(0, 0.3)

    target = premium * mult
    gain = ((target - premium) / premium) * 100

    return {
        'current_premium': round(premium, 2),
        'target_premium': round(target, 2),
        'gain_pct': round(gain, 1),
        'moneyness': round(moneyness, 3),
        'is_itm': is_itm,
        'trend_aligned': (opt_type == 'CE' and trend == 'BULLISH') or (opt_type == 'PE' and trend == 'BEARISH')
    }

def generate_fno_opportunities():
    expiry_dates = get_next_expiry_dates()
    index_data = fetch_current_index_prices()
    fno_list_url = "https://archives.nseindia.com/content/fo/fo_mktlots.csv"
    fno_df = pd.read_csv(fno_list_url)
    fno_stocks = fno_df['SYMBOL'].dropna().unique().tolist()
    stock_data = fetch_stock_prices(fno_stocks)
    recs = []

    for idx in ['NIFTY', 'BANKNIFTY']:
        px = index_data[idx]['price']
        tr = index_data[idx]['trend']
        strikes = get_correct_strike_prices(px, 'index', num_strikes=3)
        exp_days = (expiry_dates['nifty'] if idx == 'NIFTY' else expiry_dates['banknifty'] - datetime.now()).days
        opt_type = 'CE' if tr == 'BULLISH' else 'PE'

        for strike in strikes:
            data = calculate_option_targets(px, strike, opt_type, exp_days, idx, tr)
            if data['trend_aligned'] and 20 <= data['gain_pct'] <= 150:
                if not any(r['Index/Stock'] == idx and r['Strike'] == strike and r['Type'] == opt_type for r in recs):
                    recs.append({
                        'Index/Stock': idx,
                        'Current Price': px,
                        'Strike': int(strike),
                                                'Type': opt_type,
                        'LTP': data['current_premium'],
                        'Target': data['target_premium'],
                        '% Gain': data['gain_pct'],
                        'Days to Expiry': exp_days,
                        'Expiry Date': expiry_dates['nifty'].strftime('%d-%b-%Y') if idx == 'NIFTY' else expiry_dates['banknifty'].strftime('%d-%b-%Y'),
                        'Moneyness': 'ATM' if abs(data['moneyness'] - 1) < 0.02 else ('ITM' if data['is_itm'] else 'OTM'),
                        'Strategy': f"{'Bullish' if opt_type == 'CE' else 'Bearish'} on {idx} (above/below {px:.0f})",
                        'Recommendation': f"BUY {opt_type} - {'Uptrend' if opt_type == 'CE' else 'Downtrend'} Play",
                        'Risk Level': 'Medium'
                    })

    for stock in fno_stocks[:30]:
        info = stock_data.get(stock)
        if not info: continue
        px, tr, mom = info['price'], info['trend'], info['momentum']
        if tr == 'BULLISH' and mom > 0.01:
            opt_type, strat, reco = 'CE', f"{stock} bullish momentum", f"BUY CE - {stock} Upside"
        elif tr == 'BEARISH' and mom < -0.01:
            opt_type, strat, reco = 'PE', f"{stock} bearish breakdown", f"BUY PE - {stock} Downside"
        else:
            continue

        for strike in get_correct_strike_prices(px, 'stock', 2):
            data = calculate_option_targets(px, strike, opt_type, (expiry_dates['stocks'] - datetime.now()).days, stock, tr)
            if data['trend_aligned'] and 25 <= data['gain_pct'] <= 120:
                recs.append({
                    'Index/Stock': stock,
                    'Current Price': px,
                    'Strike': int(strike),
                    'Type': opt_type,
                    'LTP': data['current_premium'],
                    'Target': data['target_premium'],
                    '% Gain': data['gain_pct'],
                    'Days to Expiry': (expiry_dates['stocks'] - datetime.now()).days,
                    'Expiry Date': expiry_dates['stocks'].strftime('%d-%b-%Y'),
                    'Moneyness': 'ATM' if abs(data['moneyness'] - 1) < 0.02 else ('ITM' if data['is_itm'] else 'OTM'),
                    'Strategy': strat,
                    'Recommendation': reco,
                    'Risk Level': 'High'
                })

    df = pd.DataFrame(recs)
    if not df.empty:
        # Sort by Risk Level (Medium first) and then by % Gain
        df['risk_sort'] = df['Risk Level'].map({'Medium': 0, 'High': 1})
        df = df.sort_values(['risk_sort', '% Gain'], ascending=[True, False]).drop('risk_sort', axis=1)
    return df
