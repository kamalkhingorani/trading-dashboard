#!/usr/bin/env python3
"""
F&O Options Trading Bot - Reversal Based Strategy
Version: 5.0 CORRECTED
Date: 14-July-2025

STRATEGY:
- Trade on candle color reversal with body confirmation
- Exit immediately on opposite color candle
- One position at a time across all symbols
- Quick scalping based on momentum reversals
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
import pytz
import time as tm
import logging
from typing import Dict, List, Tuple, Optional
import math
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class ReversalOptionsTrader:
    """
    Reversal-based options trading system
    Trades on candle color changes with immediate exit on reversal
    """
    
    def __init__(self):
        self.ist = pytz.timezone('Asia/Kolkata')
        self.active_position = None  # Only ONE position at a time
        self.last_candle_color = {}  # Track last candle color for each symbol
        self.trade_history = []
        self.daily_pnl = 0
        
        # Market specifications
        self.market_specs = {
            'NIFTY': {
                'lot_size': 50,
                'strike_interval': 50,
                'symbol': '^NSEI',
                'trading_symbol': 'NIFTY'
            },
            'BANKNIFTY': {
                'lot_size': 25,
                'strike_interval': 100,
                'symbol': '^NSEBANK',
                'trading_symbol': 'BANKNIFTY'
            }
        }
        
        # Strategy parameters
        self.max_loss_per_trade = 1000  # ₹1000 max loss per trade
        self.profit_target = 1500       # ₹1500 profit target
        self.enable_reversal_exit = True  # Exit on color reversal
        
        logger.info("="*60)
        logger.info("REVERSAL OPTIONS TRADING BOT INITIALIZED")
        logger.info("Strategy: Trade on color reversal, exit on opposite color")
        logger.info("Max positions: 1 at a time")
        logger.info("="*60)
    
    def get_market_config(self, symbol: str) -> Dict:
        """Get market configuration for a symbol"""
        for market, config in self.market_specs.items():
            if config['symbol'] == symbol:
                return config
        return None
    
    def calculate_current_expiry(self) -> Tuple[str, int]:
        """Calculate current weekly expiry (Thursday)"""
        today = datetime.now(self.ist).date()
        days_to_thursday = (3 - today.weekday()) % 7
        
        if days_to_thursday == 0:  # Today is Thursday
            current_time = datetime.now(self.ist).time()
            if current_time > time(15, 30):
                days_to_thursday = 7
        
        expiry_date = today + timedelta(days=days_to_thursday)
        return expiry_date.strftime('%d%b').upper(), days_to_thursday
    
    def get_atm_strike(self, spot_price: float, strike_interval: int) -> int:
        """Get ATM strike price"""
        return round(spot_price / strike_interval) * strike_interval
    
    def calculate_option_premium(self, spot: float, strike: int, days_to_expiry: int,
                               option_type: str, volatility: float = 0.15) -> float:
        """Calculate realistic option premium"""
        time_value = spot * volatility * math.sqrt(days_to_expiry / 365) * 0.4
        
        if option_type == 'PE':
            intrinsic = max(0, strike - spot)
        else:
            intrinsic = max(0, spot - strike)
        
        # Adjust time value for moneyness
        moneyness = abs(spot - strike) / spot
        if moneyness < 0.005:  # ATM
            time_value *= 1.0
        elif moneyness < 0.01:  # Near ATM
            time_value *= 0.8
        else:  # OTM
            time_value *= 0.5
        
        premium = intrinsic + time_value
        return round(premium * 20) / 20  # Round to 0.05
    
    def fetch_candle_data(self, symbol: str) -> Optional[Dict]:
        """Fetch current candle data"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period='5d', interval='1h', prepost=False)
            
            if df.empty or len(df) < 2:
                return None
            
            current = df.iloc[-1]
            previous = df.iloc[-2]
            
            # Calculate candle metrics
            body_size = abs(current['Close'] - current['Open'])
            full_range = current['High'] - current['Low']
            
            candle_data = {
                'symbol': symbol,
                'timestamp': df.index[-1],
                'open': round(current['Open'], 2),
                'high': round(current['High'], 2),
                'low': round(current['Low'], 2),
                'close': round(current['Close'], 2),
                'color': 'GREEN' if current['Close'] >= current['Open'] else 'RED',
                'prev_color': 'GREEN' if previous['Close'] >= previous['Open'] else 'RED',
                'body_percent': round((body_size / full_range * 100) if full_range > 0 else 0, 1),
                'has_body': body_size > (full_range * 0.5) if full_range > 0 else False,
                'volume': current['Volume']
            }
            
            # Calculate EMA20
            if len(df) >= 20:
                candle_data['ema20'] = round(df['Close'].ewm(span=20).mean().iloc[-1], 2)
            else:
                candle_data['ema20'] = round(df['Close'].mean(), 2)
            
            return candle_data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def check_reversal_signal(self, symbol: str, candle_data: Dict) -> Tuple[bool, str]:
        """
        Check for reversal signal
        Returns: (has_reversal, direction)
        """
        # First time seeing this symbol
        if symbol not in self.last_candle_color:
            self.last_candle_color[symbol] = candle_data['prev_color']
        
        last_color = self.last_candle_color[symbol]
        current_color = candle_data['color']
        
        # Update last color
        self.last_candle_color[symbol] = current_color
        
        # Check for reversal with body confirmation
        if last_color != current_color and candle_data['has_body']:
            if current_color == 'GREEN':
                return True, 'BULLISH'  # Red to Green = Bullish reversal
            else:
                return True, 'BEARISH'  # Green to Red = Bearish reversal
        
        return False, 'NONE'
    
    def should_exit_position(self, position: Dict, current_candle: Dict) -> Tuple[bool, str]:
        """Check if position should be exited"""
        if not position or position['status'] != 'ACTIVE':
            return False, ''
        
        # Check color reversal exit
        if self.enable_reversal_exit:
            position_direction = 'BEARISH' if position['option_type'] == 'PE' else 'BULLISH'
            current_direction = 'BULLISH' if current_candle['color'] == 'GREEN' else 'BEARISH'
            
            if position_direction != current_direction and current_candle['has_body']:
                return True, 'COLOR_REVERSAL'
        
        # Check stop loss (monetary)
        if position['unrealized_pnl'] <= -self.max_loss_per_trade:
            return True, 'STOP_LOSS'
        
        # Check profit target
        if position['unrealized_pnl'] >= self.profit_target:
            return True, 'PROFIT_TARGET'
        
        return False, ''
    
    def execute_entry(self, symbol: str, signal_direction: str, spot_price: float) -> Optional[Dict]:
        """Execute option entry trade"""
        try:
            # Check if we already have a position
            if self.active_position and self.active_position['status'] == 'ACTIVE':
                logger.warning("Already have an active position. Skipping new entry.")
                return None
            
            # Get market config
            config = self.get_market_config(symbol)
            if not config:
                return None
            
            # Determine option type based on signal
            option_type = 'CE' if signal_direction == 'BULLISH' else 'PE'
            
            # Get expiry and strike
            expiry, days_to_expiry = self.calculate_current_expiry()
            strike = self.get_atm_strike(spot_price, config['strike_interval'])
            
            # Calculate premium
            premium = self.calculate_option_premium(spot_price, strike, days_to_expiry, option_type)
            
            # Create option symbol
            option_symbol = f"{config['trading_symbol']}{expiry}{strike}{option_type}"
            
            # Create position
            position = {
                'position_id': f"POS_{datetime.now(self.ist).strftime('%H%M%S')}",
                'underlying_symbol': symbol,
                'option_symbol': option_symbol,
                'option_type': option_type,
                'strike': strike,
                'expiry': expiry,
                'signal_direction': signal_direction,
                'entry_spot': spot_price,
                'entry_premium': premium,
                'current_premium': premium,
                'entry_time': datetime.now(self.ist),
                'lot_size': config['lot_size'],
                'quantity': config['lot_size'],  # 1 lot
                'investment': premium * config['lot_size'],
                'unrealized_pnl': 0,
                'status': 'ACTIVE'
            }
            
            self.active_position = position
            
            # Log entry
            logger.info("="*60)
            logger.info(f"OPTION POSITION ENTERED - {signal_direction} REVERSAL")
            logger.info(f"Underlying: {symbol} @ ₹{spot_price:,.2f}")
            logger.info(f"Option: {option_symbol}")
            logger.info(f"Premium: ₹{premium} × {config['lot_size']} = ₹{position['investment']:,.2f}")
            logger.info(f"Max Risk: ₹{self.max_loss_per_trade}")
            logger.info(f"Target: ₹{self.profit_target}")
            logger.info("="*60)
            
            return position
            
        except Exception as e:
            logger.error(f"Error executing entry: {e}")
            return None
    
    def update_position_value(self, position: Dict, current_spot: float) -> float:
        """Update option premium based on spot movement"""
        if not position or position['status'] != 'ACTIVE':
            return 0
        
        # Calculate spot movement
        spot_change = current_spot - position['entry_spot']
        
        # Simple delta calculation
        if position['option_type'] == 'PE':
            # PUT loses value when spot rises
            delta = -0.5
            premium_change = delta * spot_change
        else:  # CE
            # CALL gains value when spot rises
            delta = 0.5
            premium_change = delta * spot_change
        
        # Add time decay (minimal for intraday)
        hours_elapsed = (datetime.now(self.ist) - position['entry_time']).seconds / 3600
        time_decay = position['entry_premium'] * 0.02 * (hours_elapsed / 6)  # 2% per 6 hours
        
        # Calculate new premium
        new_premium = position['entry_premium'] + premium_change - time_decay
        new_premium = max(0.05, round(new_premium * 20) / 20)
        
        # Update position
        position['current_premium'] = new_premium
        position['unrealized_pnl'] = (new_premium - position['entry_premium']) * position['lot_size']
        
        return new_premium
    
    def execute_exit(self, position: Dict, exit_reason: str, exit_premium: float = None):
        """Execute option exit trade"""
        if not position or position['status'] != 'ACTIVE':
            return
        
        # Use current premium if not specified
        if exit_premium is None:
            exit_premium = position['current_premium']
        
        # Calculate final P&L
        pnl = (exit_premium - position['entry_premium']) * position['lot_size']
        roi = (pnl / position['investment']) * 100
        
        # Update position
        position['status'] = 'CLOSED'
        position['exit_premium'] = exit_premium
        position['exit_time'] = datetime.now(self.ist)
        position['exit_reason'] = exit_reason
        position['realized_pnl'] = pnl
        position['roi_percent'] = roi
        
        # Update daily P&L
        self.daily_pnl += pnl
        
        # Log exit
        logger.info("="*60)
        logger.info(f"POSITION CLOSED - {exit_reason}")
        logger.info(f"Option: {position['option_symbol']}")
        logger.info(f"Entry: ₹{position['entry_premium']} → Exit: ₹{exit_premium}")
        logger.info(f"P&L: ₹{pnl:,.2f} ({roi:.1f}%)")
        logger.info(f"Duration: {(position['exit_time'] - position['entry_time']).seconds // 60} minutes")
        logger.info(f"Daily P&L: ₹{self.daily_pnl:,.2f}")
        logger.info("="*60)
        
        # Add to history
        self.trade_history.append(position.copy())
        
        # Clear active position
        self.active_position = None
    
    def run_trading_loop(self, watchlist: List[str]):
        """Main trading loop"""
        logger.info("Starting Reversal Options Trading Bot...")
        logger.info(f"Watchlist: {watchlist}")
        logger.info(f"Max Loss: ₹{self.max_loss_per_trade} | Target: ₹{self.profit_target}")
        
        check_interval = 10  # Check every 10 seconds for quick reversals
        
        while True:
            try:
                current_time = datetime.now(self.ist)
                
                # Market hours check
                if current_time.time() < time(9, 15) or current_time.time() > time(15, 30):
                    logger.info(f"Market closed. Time: {current_time.strftime('%H:%M:%S')}")
                    tm.sleep(60)
                    continue
                
                # Fetch current data
                logger.info(f"\n[{current_time.strftime('%H:%M:%S')}] Scanning for reversals...")
                
                for symbol in watchlist:
                    candle_data = self.fetch_candle_data(symbol)
                    if not candle_data:
                        continue
                    
                    # Log current state
                    logger.info(f"{symbol}: ₹{candle_data['close']:,.2f} ({candle_data['color']}) | "
                               f"Body: {candle_data['body_percent']}% | EMA: ₹{candle_data['ema20']:,.2f}")
                    
                    # Update position value if we have one
                    if (self.active_position and 
                        self.active_position['underlying_symbol'] == symbol and
                        self.active_position['status'] == 'ACTIVE'):
                        
                        old_premium = self.active_position['current_premium']
                        new_premium = self.update_position_value(self.active_position, candle_data['close'])
                        
                        logger.info(f"Position Update: {self.active_position['option_symbol']}")
                        logger.info(f"  Spot: ₹{candle_data['close']:,.2f} (Move: {candle_data['close'] - self.active_position['entry_spot']:.2f})")
                        logger.info(f"  Premium: ₹{old_premium} → ₹{new_premium}")
                        logger.info(f"  P&L: ₹{self.active_position['unrealized_pnl']:,.2f}")
                        
                        # Check exit conditions
                        should_exit, exit_reason = self.should_exit_position(self.active_position, candle_data)
                        if should_exit:
                            logger.warning(f"Exit signal: {exit_reason}")
                            self.execute_exit(self.active_position, exit_reason)
                            continue
                    
                    # Check for new reversal signal (only if no active position)
                    if not self.active_position or self.active_position['status'] != 'ACTIVE':
                        has_reversal, direction = self.check_reversal_signal(symbol, candle_data)
                        
                        if has_reversal:
                            logger.warning(f"🔄 REVERSAL DETECTED: {symbol} turned {direction}")
                            self.execute_entry(symbol, direction, candle_data['close'])
                            break  # Only one position at a time
                
                # Show summary
                if self.active_position and self.active_position['status'] == 'ACTIVE':
                    logger.info(f"\nActive Position: {self.active_position['option_symbol']} | "
                               f"P&L: ₹{self.active_position['unrealized_pnl']:,.2f}")
                else:
                    logger.info("\nNo active positions. Waiting for reversal signal...")
                
                logger.info(f"Daily P&L: ₹{self.daily_pnl:,.2f} | Trades Today: {len(self.trade_history)}")
                
                # Wait before next check
                tm.sleep(check_interval)
                
            except KeyboardInterrupt:
                logger.info("\nShutting down...")
                if self.active_position and self.active_position['status'] == 'ACTIVE':
                    self.execute_exit(self.active_position, 'MANUAL_CLOSE')
                break
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                tm.sleep(30)

# Streamlit Dashboard
def create_dashboard():
    st.set_page_config(page_title="Reversal Options Trading", layout="wide")
    
    st.title("🔄 Reversal Options Trading Bot")
    st.caption("Trade on candle color reversals with immediate exit on opposite signal")
    
    # Initialize bot
    if 'bot' not in st.session_state:
        st.session_state.bot = ReversalOptionsTrader()
    
    bot = st.session_state.bot
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Symbol selection
        symbol_choice = st.radio(
            "Select ONE Symbol to Trade",
            options=['NIFTY', 'BANKNIFTY'],
            help="Bot trades only one symbol at a time"
        )
        
        selected_symbol = bot.market_specs[symbol_choice]['symbol']
        
        # Risk parameters
        st.divider()
        st.subheader("Risk Management")
        
        bot.max_loss_per_trade = st.number_input(
            "Max Loss per Trade (₹)",
            value=1000,
            min_value=500,
            max_value=5000,
            step=500
        )
        
        bot.profit_target = st.number_input(
            "Profit Target (₹)",
            value=1500,
            min_value=500,
            max_value=5000,
            step=500
        )
        
        bot.enable_reversal_exit = st.checkbox(
            "Exit on Color Reversal",
            value=True,
            help="Exit position when candle color reverses"
        )
        
        # Controls
        st.divider()
        if st.button("▶️ Start Trading", type="primary"):
            st.success(f"Trading {symbol_choice}! Check console for updates.")
            # In production, run in thread
            # bot.run_trading_loop([selected_symbol])
        
        if st.button("🛑 Stop Bot"):
            if bot.active_position and bot.active_position['status'] == 'ACTIVE':
                bot.execute_exit(bot.active_position, 'MANUAL_STOP')
            st.info("Bot stopped.")
    
    # Main content
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.subheader("📊 Current Position")
        if bot.active_position and bot.active_position['status'] == 'ACTIVE':
            pos = bot.active_position
            
            st.metric("Option", pos['option_symbol'])
            
            col1_1, col1_2 = st.columns(2)
            with col1_1:
                st.metric(
                    "Entry Premium",
                    f"₹{pos['entry_premium']}",
                    f"Current: ₹{pos['current_premium']}"
                )
            with col1_2:
                pnl_color = "🟢" if pos['unrealized_pnl'] >= 0 else "🔴"
                st.metric(
                    "P&L",
                    f"{pnl_color} ₹{pos['unrealized_pnl']:,.0f}",
                    f"{(pos['current_premium']/pos['entry_premium']-1)*100:.1f}%"
                )
            
            # Progress bar
            if pos['unrealized_pnl'] >= 0:
                progress = min(pos['unrealized_pnl'] / bot.profit_target, 1.0)
                st.progress(progress)
                st.caption(f"Progress to target: {progress*100:.0f}%")
            else:
                loss_progress = min(abs(pos['unrealized_pnl']) / bot.max_loss_per_trade, 1.0)
                st.progress(loss_progress)
                st.caption(f"⚠️ Loss: {loss_progress*100:.0f}% of max")
        else:
            st.info("No active position. Waiting for reversal signal...")
    
    with col2:
        st.subheader("📈 Today's Performance")
        
        col2_1, col2_2, col2_3 = st.columns(3)
        with col2_1:
            st.metric("Daily P&L", f"₹{bot.daily_pnl:,.0f}")
        with col2_2:
            st.metric("Trades", len(bot.trade_history))
        with col2_3:
            if bot.trade_history:
                wins = sum(1 for t in bot.trade_history if t['realized_pnl'] > 0)
                win_rate = (wins / len(bot.trade_history)) * 100
                st.metric("Win Rate", f"{win_rate:.0f}%")
            else:
                st.metric("Win Rate", "0%")
        
        # Recent trades
        if bot.trade_history:
            st.divider()
            st.caption("Recent Trades")
            for trade in bot.trade_history[-3:]:
                pnl_icon = "✅" if trade['realized_pnl'] > 0 else "❌"
                st.text(f"{pnl_icon} {trade['option_symbol']}: ₹{trade['realized_pnl']:,.0f} ({trade['exit_reason']})")
    
    with col3:
        st.subheader("📊 Stats")
        
        # Calculate stats
        if bot.trade_history:
            total_trades = len(bot.trade_history)
            profitable_trades = sum(1 for t in bot.trade_history if t['realized_pnl'] > 0)
            avg_win = np.mean([t['realized_pnl'] for t in bot.trade_history if t['realized_pnl'] > 0] or [0])
            avg_loss = np.mean([t['realized_pnl'] for t in bot.trade_history if t['realized_pnl'] < 0] or [0])
            
            st.metric("Avg Win", f"₹{avg_win:,.0f}")
            st.metric("Avg Loss", f"₹{abs(avg_loss):,.0f}")
            if avg_loss != 0:
                st.metric("Risk/Reward", f"{abs(avg_win/avg_loss):.1f}")
        else:
            st.info("No trades yet")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--ui":
        create_dashboard()
    else:
        # Run bot directly
        bot = ReversalOptionsTrader()
        
        # Choose ONE symbol to trade
        # Change to '^NSEBANK' for BANKNIFTY
        watchlist = ['^NSEI']  # Only NIFTY
        
        bot.run_trading_loop(watchlist)
