import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import requests
from typing import List, Dict, Tuple
import json

class USStockScanner:
    def __init__(self):
        self.sp500_symbols = self.get_sp500_symbols()
        self.nasdaq_symbols = self.get_nasdaq_100_symbols()
    
    def get_sp500_symbols(self) -> List[str]:
        """Get S&P 500 symbols"""
        try:
            # Major S&P 500 stocks for scanning
            symbols = [
                # Technology
                "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "TSLA", "META", "NVDA", 
                "NFLX", "ADBE", "CRM", "INTC", "AMD", "PYPL", "UBER", "SNOW",
                
                # Financial
                "JPM", "BAC", "WFC", "GS", "MS", "C", "AXP", "BLK", "SCHW", "USB",
                
                # Healthcare
                "JNJ", "PFE", "UNH", "ABBV", "TMO", "DHR", "BMY", "AMGN", "GILD", "MRNA",
                
                # Consumer
                "WMT", "PG", "KO", "PEP", "COST", "TGT", "HD", "LOW", "MCD", "SBUX",
                
                # Industrial
                "BA", "CAT", "GE", "MMM", "HON", "UPS", "FDX", "LMT", "RTX", "DE",
                
                # Energy
                "XOM", "CVX", "COP", "EOG", "SLB", "MPC", "VLO", "PSX", "OXY", "HAL",
                
                # Communication
                "VZ", "T", "TMUS", "CMCSA", "DIS", "NFLX", "CHTR", "VZ", "DISH", "PARA"
            ]
            return symbols
        except Exception as e:
            st.error(f"Error loading S&P 500 symbols: {e}")
            return []
    
    def get_nasdaq_100_symbols(self) -> List[str]:
        """Get NASDAQ 100 symbols for broader tech coverage"""
        try:
            nasdaq_symbols = [
                "AAPL", "MSFT", "AMZN", "GOOGL", "GOOG", "TSLA", "META", "NVDA",
                "AVGO", "ORCL", "COST", "NFLX", "ADBE", "PEP", "TMUS", "CSCO",
                "CMCSA", "TXN", "QCOM", "HON", "AMGN", "SBUX", "INTU", "AMD",
                "ISRG", "BKNG", "ADP", "GILD", "LRCX", "MU", "ADI", "PYPL",
                "REGN", "ATVI", "FISV", "CSX", "MRVL", "ORLY", "KLAC", "NXPI",
                "WDAY", "BIIB", "KDP", "ASML", "DXCM", "SGEN", "VRSK", "CTSH"
            ]
            return nasdaq_symbols
        except Exception as e:
            st.error(f"Error loading NASDAQ 100 symbols: {e}")
            return []
    
    def calculate_us_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators optimized for US markets"""
        # RSI Calculation (14-period standard)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # EMA Calculations (US market standard periods)
        data['EMA9'] = data['Close'].ewm(span=9).mean()   # Short term
        data['EMA21'] = data['Close'].ewm(span=21).mean() # Medium term
        data['EMA50'] = data['Close'].ewm(span=50).mean() # Intermediate
        data['EMA200'] = data['Close'].ewm(span=200).mean() # Long term
        
        # MACD
        exp1 = data['Close'].ewm(span=12).mean()
        exp2 = data['Close'].ewm(span=26).mean()
        data['MACD'] = exp1 - exp2
        data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
        data['MACD_Histogram'] = data['MACD'] - data['MACD_Signal']
        
        # Volume indicators
        data['Volume_MA'] = data['Volume'].rolling(window=20).mean()
        data['Volume_Ratio'] = data['Volume'] / data['Volume_MA']
        data['OBV'] = (data['Volume'] * (~data['Close'].diff().le(0) * 2 - 1)).cumsum()
        
        # Bollinger Bands
        data['BB_Middle'] = data['Close'].rolling(window=20).mean()
        bb_std = data['Close'].rolling(window=20).std()
        data['BB_Upper'] = data['BB_Middle'] + (bb_std * 2)
        data['BB_Lower'] = data['BB_Middle'] - (bb_std * 2)
        data['BB_Position'] = (data['Close'] - data['BB_Lower']) / (data['BB_Upper'] - data['BB_Lower'])
        
        # Williams %R
        high_14 = data['High'].rolling(window=14).max()
        low_14 = data['Low'].rolling(window=14).min()
        data['Williams_R'] = -100 * (high_14 - data['Close']) / (high_14 - low_14)
        
        return data
    
    def check_us_trend_alignment(self, data: pd.DataFrame) -> bool:
        """Check trend alignment for US markets"""
        latest = data.iloc[-1]
        recent = data.iloc[-10:]
        
        # Price above key EMAs
        above_ema21 = latest['Close'] > latest['EMA21']
        above_ema50 = latest['Close'] > latest['EMA50']
        
        # EMA alignment (US markets prefer 9/21/50/200 setup)
        ema_bullish = (latest['EMA9'] > latest['EMA21'] * 0.998 and
                      latest['EMA21'] > latest['EMA50'] * 0.995)
        
        # MACD bullish
        macd_bullish = (latest['MACD'] > latest['MACD_Signal'] and
                       recent['MACD_Histogram'].iloc[-1] > recent['MACD_Histogram'].iloc[-3])
        
        # RSI in momentum zone
        rsi_momentum = 30 <= latest['RSI'] <= 75
        
        # Above 200 EMA for long-term trend
        above_200ema = latest['Close'] > latest['EMA200']
        
        return above_ema21 and ema_bullish and macd_bullish and rsi_momentum and above_200ema
    
    def check_us_breakout_pattern(self, data: pd.DataFrame) -> bool:
        """Check for US market breakout patterns"""
        latest = data.iloc[-1]
        recent_5 = data.iloc[-5:]
        
        # Volume breakout (US markets are volume driven)
        volume_breakout = latest['Volume_Ratio'] > 1.3
        
        # Price breakout above Bollinger Band middle
        bb_breakout = latest['BB_Position'] > 0.6
        
        # Williams %R coming out of oversold
        williams_recovery = -50 <= latest['Williams_R'] <= -20
        
        # Consistent green candles in recent sessions
        green_momentum = sum(recent_5['Close'] > recent_5['Open']) >= 3
        
        # OBV trending up
        obv_rising = recent_5['OBV'].iloc[-1] > recent_5['OBV'].iloc[0]
        
        return volume_breakout and bb_breakout and williams_recovery and green_momentum and obv_rising
    
    def calculate_us_target_sl(self, current_price: float, data: pd.DataFrame, symbol: str) -> Tuple[float, float]:
        """Calculate target and SL for US stocks"""
        # US market volatility calculation
        returns = data['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)
        
        # US market target calculation (more conservative than Indian markets)
        if symbol in ["AAPL", "MSFT", "GOOGL", "AMZN"]:  # Large caps
            target_pct = min(12, max(4, volatility * 20))
        elif volatility > 0.4:  # High volatility stocks
            target_pct = min(18, max(6, volatility * 25))
        else:  # Regular stocks
            target_pct = min(15, max(5, volatility * 22))
        
        target = current_price * (1 + target_pct / 100)
        
        # US market SL calculation
        latest = data.iloc[-1]
        
        # Support levels
        ema21_support = latest['EMA21']
        bb_lower_support = latest['BB_Lower']
        recent_support = data['Low'].tail(20).min()
        
        # Choose highest support level
        technical_sl = max(ema21_support * 0.98, bb_lower_support * 1.01, recent_support * 0.99)
        percentage_sl = current_price * 0.94  # 6% SL for US markets
        
        stop_loss = max(technical_sl, percentage_sl)
        
        return round(target, 2), round(stop_loss, 2)
    
    def estimate_us_market_days(self, current_price: float, target: float, data: pd.DataFrame) -> int:
        """Estimate days to target for US markets"""
        returns = data['Close'].pct_change().dropna()
        
        # US markets tend to be more efficient
        positive_returns = returns[returns > 0.01]  # Filter out small moves
        if len(positive_returns) == 0:
            return 30
        
        avg_positive_return = positive_returns.mean()
        target_return = (target - current_price) / current_price
        
        if avg_positive_return <= 0:
            return 30
        
        estimated_days = target_return / avg_positive_return
        
        # US market consideration (faster moves)
        return min(20, max(2, int(estimated_days)))
    
    def get_us_fundamentals(self, symbol: str) -> Dict:
        """Get fundamental data for US stocks"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'peg_ratio': info.get('pegRatio', 0),
                'price_to_book': info.get('priceToBook', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'roe': info.get('returnOnEquity', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'beta': info.get('beta', 0),
                'dividend_yield': info.get('dividendYield', 0)
            }
        except:
            return {}
    
    def scan_us_stocks(self, min_price: float = 25, max_rsi: float = 35, 
                      min_volume: float = 1000000, use_nasdaq: bool = False) -> pd.DataFrame:
        """Main scanning function for US stocks"""
        symbols_to_scan = self.nasdaq_symbols if use_nasdaq else self.sp500_symbols
        recommendations = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Limit scanning for performance
        scan_limit = min(25, len(symbols_to_scan))
        
        for i, symbol in enumerate(symbols_to_scan[:scan_limit]):
            try:
                status_text.text(f"Scanning {symbol}... ({i+1}/{scan_limit})")
                progress_bar.progress((i + 1) / scan_limit)
                
                # Download 6 months of data
                stock = yf.Ticker(symbol)
                data = stock.history(period="6mo", interval="1d")
                
                if data.empty or len(data) < 200:
                    continue
                
                # Calculate technical indicators
                data = self.calculate_us_technical_indicators(data)
                
                latest = data.iloc[-1]
                current_price = latest['Close']
                current_rsi = latest['RSI']
                avg_volume = data['Volume'].tail(20).mean()
                
                # Apply basic filters
                if (current_price >= min_price and 
                    current_rsi <= max_rsi and 
                    avg_volume >= min_volume and
                    not pd.isna(current_rsi)):
                    
                    # Apply US market specific technical filters
                    if (self.check_us_trend_alignment(data) and 
                        self.check_us_breakout_pattern(data)):
                        
                        target, stop_loss = self.calculate_us_target_sl(current_price, data, symbol)
                        gain_pct = ((target - current_price) / current_price) * 100
                        days_estimate = self.estimate_us_market_days(current_price, target, data)
                        
                        # Get fundamental data
                        fundamentals = self.get_us_fundamentals(symbol)
                        
                        # Generate remarks
                        remarks = self.generate_us_remarks(data, fundamentals)
                        
                        recommendations.append({
                            'Date': datetime.now().strftime('%Y-%m-%d'),
                            'Stock': symbol,
                            'LTP': round(current_price, 2),
                            'RSI': round(current_rsi, 1),
                            'Target': target,
                            '% Gain': round(gain_pct, 1),
                            'Est. Days': days_estimate,
                            'Stop Loss': stop_loss,
                            'Volume Ratio': round(latest['Volume_Ratio'], 2),
                            'Sector': fundamentals.get('sector', 'Unknown'),
                            'Beta': round(fundamentals.get('beta', 0), 2),
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
    
    def generate_us_remarks(self, data: pd.DataFrame, fundamentals: Dict) -> str:
        """Generate remarks for US stocks"""
        latest = data.iloc[-1]
        remarks = []
        
        # Technical remarks
        if latest['Volume_Ratio'] > 2:
            remarks.append("Volume surge")
        elif latest['Volume_Ratio'] > 1.5:
            remarks.append("High volume")
        
        if latest['MACD'] > latest['MACD_Signal']:
            remarks.append("MACD bullish")
        
        if latest['BB_Position'] > 0.8:
            remarks.append("BB breakout")
        elif latest['BB_Position'] > 0.6:
            remarks.append("Upper BB")
        
        if -30 <= latest['Williams_R'] <= -20:
            remarks.append("Williams recovery")
        
        # Fundamental remarks
        pe_ratio = fundamentals.get('pe_ratio', 0)
        if pe_ratio and pe_ratio < 15:
            remarks.append("Low PE")
        elif pe_ratio and pe_ratio > 25:
            remarks.append("Growth stock")
        
        beta = fundamentals.get('beta', 0)
        if beta > 1.5:
            remarks.append("High beta")
        elif beta < 0.8:
            remarks.append("Low beta")
        
        return " | ".join(remarks) if remarks else "Technical breakout"

def get_us_recommendations(min_price: float = 25, max_rsi: float = 35, 
                          min_volume: float = 1000000, use_nasdaq: bool = False) -> pd.DataFrame:
    """Main function to get US stock recommendations"""
    scanner = USStockScanner()
    return scanner.scan_us_stocks(min_price, max_rsi, min_volume, use_nasdaq)

def get_us_market_overview() -> Dict:
    """Get US market overview data"""
    try:
        sp500 = yf.download("^GSPC", period="1d", interval="1m")
        nasdaq = yf.download("^IXIC", period="1d", interval="1m")
        dow = yf.download("^DJI", period="1d", interval="1m")
        
        result = {}
        
        if not sp500.empty:
            sp500_latest = sp500.iloc[-1]
            result.update({
                'sp500_price': sp500_latest['Close'],
                'sp500_change': sp500_latest['Close'] - sp500.iloc[0]['Open']
            })
        
        if not nasdaq.empty:
            nasdaq_latest = nasdaq.iloc[-1]
            result.update({
                'nasdaq_price': nasdaq_latest['Close'],
                'nasdaq_change': nasdaq_latest['Close'] - nasdaq.iloc[0]['Open']
            })
        
        if not dow.empty:
            dow_latest = dow.iloc[-1]
            result.update({
                'dow_price': dow_latest['Close'],
                'dow_change': dow_latest['Close'] - dow.iloc[0]['Open']
            })
        
        result['last_updated'] = datetime.now().strftime('%H:%M:%S')
        return result
        
    except:
        return {
            'sp500_price': 0, 'sp500_change': 0,
            'nasdaq_price': 0, 'nasdaq_change': 0,
            'dow_price': 0, 'dow_change': 0,
            'last_updated': 'Error loading data'
        }
