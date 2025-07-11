import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import requests
from typing import List, Dict, Tuple
import json

class IndianStockScanner:
    def __init__(self):
        self.nse_symbols = self.get_nse_symbols()
        self.nifty_500_symbols = self.get_nifty_500_symbols()
    
    def get_nse_symbols(self) -> List[str]:
        """Get NSE symbols from various sources"""
        try:
            # Primary NSE stocks with .NS suffix for yfinance
            symbols = [
                "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
                "ICICIBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ASIANPAINT.NS",
                "ITC.NS", "AXISBANK.NS", "LT.NS", "DMART.NS", "SUNPHARMA.NS",
                "ULTRACEMCO.NS", "TITAN.NS", "WIPRO.NS", "NESTLEIND.NS", "POWERGRID.NS",
                "NTPC.NS", "TECHM.NS", "HCLTECH.NS", "MARUTI.NS", "BAJFINANCE.NS",
                "TATASTEEL.NS", "ONGC.NS", "COALINDIA.NS", "DRREDDY.NS", "BAJAJFINSV.NS",
                "INDUSINDBK.NS", "BRITANNIA.NS", "DIVISLAB.NS", "GRASIM.NS", "HEROMOTOCO.NS",
                "JSWSTEEL.NS", "CIPLA.NS", "EICHERMOT.NS", "BPCL.NS", "HINDALCO.NS",
                "SHREECEM.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "TATACONSUM.NS", "IOC.NS",
                "TATAMOTORS.NS", "PIDILITIND.NS", "GODREJCP.NS", "ADANIENT.NS", "SBILIFE.NS"
            ]
            return symbols
        except Exception as e:
            st.error(f"Error loading NSE symbols: {e}")
            return []
    
    def get_nifty_500_symbols(self) -> List[str]:
        """Get Nifty 500 symbols - expanded list"""
        try:
            # Additional Nifty 500 stocks for broader scanning
            extended_symbols = [
                "HDFCLIFE.NS", "BAJAJ-AUTO.NS", "HAVELLS.NS", "MCDOWELL-N.NS", "DABUR.NS",
                "MARICO.NS", "COLPAL.NS", "BERGEPAINT.NS", "VOLTAS.NS", "TORNTPHARM.NS",
                "BIOCON.NS", "CADILAHC.NS", "LUPIN.NS", "AUBANK.NS", "BANDHANBNK.NS",
                "FEDERALBNK.NS", "IDFCFIRSTB.NS", "PNB.NS", "BANKINDIA.NS", "CANBK.NS",
                "M&M.NS", "ASHOKLEY.NS", "TVSMOTOR.NS", "BAJAJHLDNG.NS", "MOTHERSUMI.NS",
                "BOSCHLTD.NS", "ESCORTS.NS", "BHEL.NS", "BEL.NS", "HAL.NS",
                "SAIL.NS", "NMDC.NS", "VEDL.NS", "JINDALSTEL.NS", "RATNAMANI.NS",
                "CONCOR.NS", "IRCTC.NS", "ADANIGREEN.NS", "ADANITRANS.NS", "RPOWER.NS",
                "PAGEIND.NS", "HONAUT.NS", "SIEMENS.NS", "ABB.NS", "CUMMINSIND.NS",
                "MINDTREE.NS", "LTI.NS", "MPHASIS.NS", "COFORGE.NS", "PERSISTENT.NS"
            ]
            return self.nse_symbols + extended_symbols
        except Exception as e:
            st.error(f"Error loading Nifty 500 symbols: {e}")
            return self.nse_symbols
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI, EMAs, and other technical indicators specific to Indian markets"""
        # RSI Calculation (14-period)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # EMA Calculations (Indian market specific periods)
        data['EMA20'] = data['Close'].ewm(span=20).mean()
        data['EMA50'] = data['Close'].ewm(span=50).mean()
        data['EMA100'] = data['Close'].ewm(span=100).mean()
        data['EMA200'] = data['Close'].ewm(span=200).mean()
        
        # Volume analysis (Indian market characteristics)
        data['Volume_MA'] = data['Volume'].rolling(window=20).mean()
        data['Volume_Ratio'] = data['Volume'] / data['Volume_MA']
        
        # VWAP calculation
        data['VWAP'] = (data['Volume'] * (data['High'] + data['Low'] + data['Close']) / 3).cumsum() / data['Volume'].cumsum()
        
        # Indian market specific indicators
        data['Price_vs_VWAP'] = data['Close'] / data['VWAP']
        
        return data
    
    def check_ema_alignment_indian(self, data: pd.DataFrame) -> bool:
        """Check EMA alignment specific to Indian market patterns"""
        latest = data.iloc[-1]
        prev_5 = data.iloc[-5:]
        
        # Price above EMA20
        price_above_ema20 = latest['Close'] > latest['EMA20']
        
        # EMA20 trending upward
        ema20_rising = prev_5['EMA20'].iloc[-1] > prev_5['EMA20'].iloc[0]
        
        # EMA sequence improving (allowing for Indian market volatility)
        ema_improving = (
            latest['EMA20'] >= latest['EMA50'] * 0.995 and  # 0.5% tolerance
            latest['EMA50'] >= latest['EMA100'] * 0.99 and   # 1% tolerance
            latest['EMA100'] >= latest['EMA200'] * 0.985     # 1.5% tolerance
        )
        
        # Price momentum above VWAP
        above_vwap = latest['Price_vs_VWAP'] > 1.0
        
        return price_above_ema20 and ema20_rising and ema_improving and above_vwap
    
    def is_bullish_pattern_indian(self, data: pd.DataFrame) -> bool:
        """Check for bullish patterns in Indian stocks"""
        latest_3 = data.iloc[-3:].copy()
        
        # Calculate candle properties
        for i in range(len(latest_3)):
            idx = latest_3.index[i]
            open_price = latest_3.loc[idx, 'Open']
            close_price = latest_3.loc[idx, 'Close']
            high_price = latest_3.loc[idx, 'High']
            low_price = latest_3.loc[idx, 'Low']
            
            latest_3.loc[idx, 'Body'] = abs(close_price - open_price)
            latest_3.loc[idx, 'Upper_Shadow'] = high_price - max(close_price, open_price)
            latest_3.loc[idx, 'Lower_Shadow'] = min(close_price, open_price) - low_price
            latest_3.loc[idx, 'Is_Green'] = close_price > open_price
        
        latest = latest_3.iloc[-1]
        prev = latest_3.iloc[-2]
        
        # Current candle is green
        current_green = latest['Is_Green']
        
        # Volume confirmation (Indian markets love volume)
        volume_breakout = latest['Volume_Ratio'] > 1.5
        
        # Body size significance (not a doji)
        significant_body = latest['Body'] > (latest['High'] - latest['Low']) * 0.3
        
        # RSI in sweet spot (not overbought but showing momentum)
        rsi_sweet_spot = 25 <= latest_3['RSI'].iloc[-1] <= 70
        
        return current_green and volume_breakout and significant_body and rsi_sweet_spot
    
    def calculate_indian_target_sl(self, current_price: float, data: pd.DataFrame, symbol: str) -> Tuple[float, float]:
        """Calculate target and SL levels for Indian stocks"""
        # Indian market volatility adjustment
        returns = data['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)
        
        # Target calculation (Indian market expectations)
        if volatility > 0.5:  # High volatility stock
            target_pct = min(20, max(8, volatility * 25))
        else:  # Low volatility stock
            target_pct = min(15, max(5, volatility * 30))
        
        target = current_price * (1 + target_pct / 100)
        
        # SL calculation using Indian market support levels
        recent_support = data['Low'].tail(30).min()  # 30-day support
        ema20_support = data['EMA20'].iloc[-1]
        vwap_support = data['VWAP'].iloc[-1]
        
        # Use highest of recent support levels
        technical_sl = max(recent_support * 0.98, ema20_support * 0.97, vwap_support * 0.98)
        percentage_sl = current_price * 0.92  # 8% SL for Indian markets
        
        stop_loss = max(technical_sl, percentage_sl)
        
        # Round to Indian rupee precision
        return round(target, 2), round(stop_loss, 2)
    
    def estimate_days_indian_market(self, current_price: float, target: float, data: pd.DataFrame) -> int:
        """Estimate days to target considering Indian market characteristics"""
        returns = data['Close'].pct_change().dropna()
        
        # Indian market tends to have higher volatility
        positive_returns = returns[returns > 0]
        if len(positive_returns) == 0:
            return 30
        
        avg_positive_return = positive_returns.mean()
        target_return = (target - current_price) / current_price
        
        if avg_positive_return <= 0:
            return 30
        
        estimated_days = target_return / avg_positive_return
        
        # Indian market cycles consideration
        return min(25, max(3, int(estimated_days)))
    
    def get_stock_fundamentals(self, symbol: str) -> Dict:
        """Get basic fundamental data for Indian stocks"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'book_value': info.get('bookValue', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'sector': info.get('sector', 'Unknown')
            }
        except:
            return {}
    
    def scan_indian_stocks(self, min_price: float = 25, max_rsi: float = 35, 
                          min_volume: float = 100000, use_nifty500: bool = True) -> pd.DataFrame:
        """Main scanning function for Indian stocks"""
        symbols_to_scan = self.nifty_500_symbols if use_nifty500 else self.nse_symbols
        recommendations = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Limit scanning for demo/performance
        scan_limit = min(30, len(symbols_to_scan))
        
        for i, symbol in enumerate(symbols_to_scan[:scan_limit]):
            try:
                status_text.text(f"Scanning {symbol.replace('.NS', '')}... ({i+1}/{scan_limit})")
                progress_bar.progress((i + 1) / scan_limit)
                
                # Download 6 months of data
                stock = yf.Ticker(symbol)
                data = stock.history(period="6mo", interval="1d")
                
                if data.empty or len(data) < 200:
                    continue
                
                # Calculate technical indicators
                data = self.calculate_technical_indicators(data)
                
                latest = data.iloc[-1]
                current_price = latest['Close']
                current_rsi = latest['RSI']
                avg_volume = data['Volume'].tail(20).mean()
                
                # Apply basic filters
                if (current_price >= min_price and 
                    current_rsi <= max_rsi and 
                    avg_volume >= min_volume and
                    not pd.isna(current_rsi)):
                    
                    # Apply Indian market specific technical filters
                    if (self.check_ema_alignment_indian(data) and 
                        self.is_bullish_pattern_indian(data)):
                        
                        target, stop_loss = self.calculate_indian_target_sl(current_price, data, symbol)
                        gain_pct = ((target - current_price) / current_price) * 100
                        days_estimate = self.estimate_days_indian_market(current_price, target, data)
                        
                        # Get fundamental data
                        fundamentals = self.get_stock_fundamentals(symbol)
                        
                        # Generate remarks based on technical setup
                        remarks = self.generate_remarks(data, fundamentals)
                        
                        recommendations.append({
                            'Date': datetime.now().strftime('%Y-%m-%d'),
                            'Stock': symbol.replace('.NS', ''),
                            'LTP': round(current_price, 2),
                            'RSI': round(current_rsi, 1),
                            'Target': target,
                            '% Gain': round(gain_pct, 1),
                            'Est. Days': days_estimate,
                            'Stop Loss': stop_loss,
                            'Volume Ratio': round(latest['Volume_Ratio'], 2),
                            'Sector': fundamentals.get('sector', 'Unknown'),
                            'Remarks': remarks,
                            'Status': 'Active'
                        })
                        
            except Exception as e:
                continue
        
        progress_bar.empty()
        status_text.empty()
        
        # Sort by % Gain potential
        df = pd.DataFrame(recommendations)
        if not df.empty:
            df = df.sort_values('% Gain', ascending=False)
        
        return df
    
    def generate_remarks(self, data: pd.DataFrame, fundamentals: Dict) -> str:
        """Generate intelligent remarks based on technical and fundamental analysis"""
        latest = data.iloc[-1]
        remarks = []
        
        # Technical remarks
        if latest['Volume_Ratio'] > 2:
            remarks.append("High volume breakout")
        elif latest['Volume_Ratio'] > 1.5:
            remarks.append("Above avg volume")
        
        if latest['RSI'] < 30:
            remarks.append("Oversold bounce")
        elif latest['RSI'] < 40:
            remarks.append("RSI recovery")
        
        if latest['Price_vs_VWAP'] > 1.02:
            remarks.append("Above VWAP")
        
        # EMA remarks
        if (latest['EMA20'] > latest['EMA50'] > latest['EMA100'] > latest['EMA200']):
            remarks.append("Perfect EMA stack")
        else:
            remarks.append("EMA alignment improving")
        
        # Fundamental remarks
        pe_ratio = fundamentals.get('pe_ratio', 0)
        if pe_ratio and pe_ratio < 15:
            remarks.append("Low PE")
        elif pe_ratio and pe_ratio > 30:
            remarks.append("Growth premium")
        
        return " | ".join(remarks) if remarks else "Technical breakout setup"

def get_indian_recommendations(min_price: float = 25, max_rsi: float = 35, 
                             min_volume: float = 100000, use_nifty500: bool = True) -> pd.DataFrame:
    """Main function to get Indian stock recommendations"""
    scanner = IndianStockScanner()
    return scanner.scan_indian_stocks(min_price, max_rsi, min_volume, use_nifty500)

# Utility functions for the dashboard
def update_recommendation_status(df: pd.DataFrame, index: int, new_status: str) -> pd.DataFrame:
    """Update the status of a recommendation"""
    df.loc[index, 'Status'] = new_status
    df.loc[index, 'Updated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    return df

def get_indian_market_overview() -> Dict:
    """Get Indian market overview data"""
    try:
        nifty = yf.download("^NSEI", period="1d", interval="1m")
        sensex = yf.download("^BSESN", period="1d", interval="1m")
        
        if not nifty.empty and not sensex.empty:
            nifty_latest = nifty.iloc[-1]
            sensex_latest = sensex.iloc[-1]
            
            return {
                'nifty_price': nifty_latest['Close'],
                'nifty_change': nifty_latest['Close'] - nifty.iloc[0]['Open'],
                'sensex_price': sensex_latest['Close'],
                'sensex_change': sensex_latest['Close'] - sensex.iloc[0]['Open'],
                'last_updated': datetime.now().strftime('%H:%M:%S')
            }
    except:
        pass
    
    return {
        'nifty_price': 0,
        'nifty_change': 0,
        'sensex_price': 0,
        'sensex_change': 0,
        'last_updated': 'Error loading data'
    }
