import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import time

# Import our custom modules
from indian_stock_logic import get_indian_recommendations, get_indian_market_overview
from us_stock_logic import get_us_recommendations, get_us_market_overview  
from news_logic import get_latest_news
from fixed_fno_options_logic import generate_fno_opportunities, get_options_summary

# Page configuration
st.set_page_config(
    page_title="Kamal's Trading Dashboard",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .news-item {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    .batch-info {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .opportunity-alert {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .risk-info {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'indian_recos' not in st.session_state:
    st.session_state.indian_recos = pd.DataFrame()
if 'us_recos' not in st.session_state:
    st.session_state.us_recos = pd.DataFrame()
if 'fno_recos' not in st.session_state:
    st.session_state.fno_recos = pd.DataFrame()
if 'news_data' not in st.session_state:
    st.session_state.news_data = []
if 'scan_count' not in st.session_state:
    st.session_state.scan_count = 0

# Main title
st.markdown('<h1 class="main-header">📈 Kamal\'s Trading Dashboard</h1>', unsafe_allow_html=True)

# Professional info
st.markdown("""
<div class="opportunity-alert">
<strong>💼 Professional Trading Assistant</strong><br>
🔄 <strong>Dynamic Analysis</strong>: Real-time calculations with proper risk management<br>
📊 <strong>Risk-Reward Focus</strong>: Minimum 1:2 ratio on all recommendations<br>
⏰ <strong>Market Coverage</strong>: Indian (NSE) and US (S&P 500) markets<br>
💰 <strong>F&O Options</strong>: Directional strategies with correct Indian market structure
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Dashboard Controls")
st.sidebar.info("""
**🎯 Features**
• Dynamic targets based on volatility
• Proper stop-loss calculation
• Technical scoring system
• Real-time news with IST
• Single-direction F&O trades

**📊 Risk Management**
• SL ≤ 50% of target gain
• Minimum 1:2 risk-reward
• Technical confirmation
• Trend-based filtering
""")

if st.sidebar.button("🔄 Refresh All Data"):
    st.session_state.indian_recos = pd.DataFrame()
    st.session_state.us_recos = pd.DataFrame()
    st.session_state.fno_recos = pd.DataFrame()
    st.session_state.news_data = []
    st.success("All data refreshed!")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📰 Market News", 
    "🇮🇳 Indian Stocks", 
    "🇺🇸 US Stocks", 
    "📊 F&O Options"
])

# Tab 1: Market News
with tab1:
    st.subheader("📰 Market News & Analysis")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        <div class="batch-info">
        <strong>📡 Live News Feed</strong><br>
        Real-time market news from multiple sources with IST timestamps and impact analysis
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("🔄 Load Latest News", type="primary") or not st.session_state.news_data:
        with st.spinner("Fetching latest market news..."):
            st.session_state.news_data = get_latest_news()
            if st.session_state.news_data:
                st.success(f"Loaded {len(st.session_state.news_data)} news items!")
            else:
                st.warning("No recent news found. Please check your internet connection.")
    
    if st.session_state.news_data:
        # News summary
        high_impact = len([n for n in st.session_state.news_data if n['market_impact'] == 'High'])
        medium_impact = len([n for n in st.session_state.news_data if n['market_impact'] == 'Medium'])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total News", len(st.session_state.news_data))
        with col2:
            st.metric("High Impact", high_impact, delta=None, delta_color="inverse")
        with col3:
            st.metric("Medium Impact", medium_impact)
        with col4:
            st.metric("Updated", datetime.now().strftime('%H:%M IST'))
        
        # Display news items
        for news in st.session_state.news_data:
            impact_color = {'High': '#dc3545', 'Medium': '#fd7e14', 'Low': '#28a745'}[news['market_impact']]
            
            st.markdown(f"""
            <div class="news-item">
                <h4 style="margin-bottom: 0.5rem;">{news['title']}</h4>
                <div style="display: flex; gap: 1rem; margin-bottom: 0.5rem;">
                    <span style="color: {impact_color}; font-weight: bold;">● {news['market_impact']} Impact</span>
                    <span><strong>Category:</strong> {news['category']}</span>
                    <span><strong>Source:</strong> {news['source']}</span>
                </div>
                <p style="color: #555; margin-bottom: 0.5rem;">{news['summary']}</p>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <small>📅 {news['date']} | ⏰ {news['time']}</small>
                    <a href="{news['link']}" target="_blank" style="background-color: #1f77b4; color: white; padding: 5px 15px; text-decoration: none; border-radius: 3px; font-size: 12px;">Read More →</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Tab 2: Indian Stocks
with tab2:
    st.subheader("🇮🇳 Indian Stock Recommendations")
    
    st.markdown("""
    <div class="batch-info">
    <strong>📊 NSE Stock Scanner</strong><br>
    Dynamic targets based on volatility | Proper risk management | Technical scoring
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        min_price_in = st.number_input("Min Price (₹)", value=100, min_value=1, key="in_price")
    with col2:
        max_rsi_in = st.number_input("Max RSI", value=60, min_value=1, max_value=100, key="in_rsi")
    with col3:
        batch_size_in = st.number_input("Batch Size", value=30, min_value=10, max_value=100, key="in_batch")
    
    if st.button("🔍 Scan Indian Stocks", type="primary"):
        with st.spinner("Scanning NSE stocks with dynamic analysis..."):
            st.session_state.indian_recos = get_indian_recommendations(
                min_price=min_price_in, 
                max_rsi=max_rsi_in,
                batch_size=batch_size_in
            )
            st.session_state.scan_count += 1
            
            if not st.session_state.indian_recos.empty:
                st.success(f"🎯 Found {len(st.session_state.indian_recos)} opportunities with proper risk-reward!")
            else:
                st.warning("No stocks found. Try adjusting filters or increasing batch size.")
    
    if not st.session_state.indian_recos.empty:
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Opportunities", len(st.session_state.indian_recos))
        with col2:
            avg_gain = st.session_state.indian_recos['% Gain'].mean()
            st.metric("Avg Target", f"{avg_gain:.1f}%")
        with col3:
            avg_days = st.session_state.indian_recos['Est. Days'].mean()
            st.metric("Avg Days", f"{avg_days:.0f}")
        with col4:
            high_score = len(st.session_state.indian_recos[st.session_state.indian_recos['Tech Score'] >= '4/5'])
            st.metric("High Score", high_score)
        
        # Risk info
        st.markdown("""
        <div class="risk-info">
        <strong>⚠️ Risk Management Applied</strong><br>
        • Stop Loss ≤ 50% of potential gain (ensures minimum 1:2 risk-reward)<br>
        • Dynamic targets based on volatility and technical factors<br>
        • Only showing stocks with Risk:Reward ratio ≥ 2.0
        </div>
        """, unsafe_allow_html=True)
        
        # Display recommendations
        st.dataframe(
            st.session_state.indian_recos,
            use_container_width=True,
            height=400,
            column_config={
                "% Gain": st.column_config.NumberColumn("% Gain", format="%.1f%%"),
                "SL %": st.column_config.NumberColumn("SL %", format="%.1f%%"),
                "Risk:Reward": st.column_config.TextColumn("Risk:Reward", help="Ratio of potential gain to risk"),
                "Tech Score": st.column_config.TextColumn("Tech Score", help="Technical indicators score"),
                "Volatility": st.column_config.TextColumn("Volatility", help="Annualized volatility")
            }
        )
        
        # Download option
        csv = st.session_state.indian_recos.to_csv(index=False)
        st.download_button(
            "📥 Download Indian Recommendations",
            csv,
            f"indian_stocks_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv"
        )

# Tab 3: US Stocks
with tab3:
    st.subheader("🇺🇸 US Stock Recommendations")
    
    st.markdown("""
    <div class="batch-info">
    <strong>📊 S&P 500 Stock Scanner</strong><br>
    Tighter ranges for efficient US markets | 6-point technical scoring | Market cap based filtering
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        min_price_us = st.number_input("Min Price ($)", value=50, min_value=1, key="us_price")
    with col2:
        max_rsi_us = st.number_input("Max RSI", value=60, min_value=1, max_value=100, key="us_rsi")
    with col3:
        batch_size_us = st.number_input("Batch Size", value=30, min_value=10, max_value=100, key="us_batch")
    
    if st.button("🔍 Scan US Stocks", type="primary"):
        with st.spinner("Scanning S&P 500 stocks with advanced analysis..."):
            st.session_state.us_recos = get_us_recommendations(
                min_price=min_price_us,
                max_rsi=max_rsi_us,
                batch_size=batch_size_us
            )
            st.session_state.scan_count += 1
            
            if not st.session_state.us_recos.empty:
                st.success(f"🎯 Found {len(st.session_state.us_recos)} opportunities with strong technicals!")
            else:
                st.warning("No stocks found. Try adjusting filters or increasing batch size.")
    
    if not st.session_state.us_recos.empty:
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Opportunities", len(st.session_state.us_recos))
        with col2:
            avg_gain = st.session_state.us_recos['% Gain'].mean()
            st.metric("Avg Target", f"{avg_gain:.1f}%")
        with col3:
            large_cap = len(st.session_state.us_recos[st.session_state.us_recos['Market Cap'] == 'Large Cap'])
            st.metric("Large Cap", large_cap)
        with col4:
            high_score = len(st.session_state.us_recos[st.session_state.us_recos['Tech Score'] >= '5/6'])
            st.metric("High Score", high_score)
        
        # Display recommendations
        st.dataframe(
            st.session_state.us_recos,
            use_container_width=True,
            height=400,
            column_config={
                "% Gain": st.column_config.NumberColumn("% Gain", format="%.1f%%"),
                "SL %": st.column_config.NumberColumn("SL %", format="%.1f%%"),
                "Risk:Reward": st.column_config.TextColumn("Risk:Reward", help="Ratio of potential gain to risk"),
                "Tech Score": st.column_config.TextColumn("Tech Score", help="Technical indicators score (out of 6)"),
                "BB Position": st.column_config.TextColumn("BB Position", help="Position within Bollinger Bands (0-1)")
            }
        )
        
        # Download option
        csv = st.session_state.us_recos.to_csv(index=False)
        st.download_button(
            "📥 Download US Recommendations",
            csv,
            f"us_stocks_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv"
        )

# Tab 4: F&O Options
with tab4:
    st.subheader("📊 F&O Options Trading")
    
    st.markdown("""
    <div class="batch-info">
    <strong>📈 Directional Options Trading</strong><br>
    • <strong>Single Direction</strong>: Only CE for bullish or PE for bearish - not both<br>
    • <strong>Trend Based</strong>: Recommendations align with underlying trend<br>
    • <strong>Correct Structure</strong>: Proper strikes and expiries per Indian market rules
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    if st.button("🔍 Generate F&O Opportunities", type="primary"):
        with st.spinner("Analyzing indices and stocks for directional opportunities..."):
            st.session_state.fno_recos = generate_fno_opportunities()
            st.session_state.scan_count += 1
            
            if not st.session_state.fno_recos.empty:
                st.success(f"🎯 Generated {len(st.session_state.fno_recos)} directional opportunities!")
            else:
                st.warning("No opportunities found. Market may be in consolidation.")
    
    if not st.session_state.fno_recos.empty:
        # Get summary
        summary = get_options_summary(st.session_state.fno_recos)
        
        # Display market view
        market_view_color = "#28a745" if summary['bullish_bias'] else "#dc3545"
        st.markdown(f"""
        <div style="background-color: {market_view_color}20; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid {market_view_color}; margin-bottom: 1rem;">
        <h3 style="margin: 0;">Market View: {summary['market_view']}</h3>
        <p style="margin: 0.5rem 0 0 0;">CE Options: {summary['ce_count']} | PE Options: {summary['pe_count']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Opportunities", summary['total_opportunities'])
        with col2:
            st.metric("Avg Gain Potential", f"{summary['avg_gain_potential']:.1f}%")
        with col3:
            st.metric("NIFTY/BANKNIFTY", summary['nifty_options'] + summary['banknifty_options'])
        with col4:
            st.metric("Stock Options", summary['stock_options'])
        
        # Display recommendations
        st.dataframe(
            st.session_state.fno_recos,
            use_container_width=True,
            height=400,
            column_config={
                "% Gain": st.column_config.NumberColumn("% Gain", format="%.1f%%"),
                "Current Price": st.column_config.NumberColumn("Current Price", format="%.2f"),
                "Strike": st.column_config.NumberColumn("Strike", format="%d"),
                "LTP": st.column_config.NumberColumn("LTP", format="%.2f"),
                "Target": st.column_config.NumberColumn("Target", format="%.2f")
            }
        )
        
        # Important notes
        st.markdown("""
        <div class="risk-info">
        <strong>⚠️ F&O Trading Guidelines</strong><br>
        • <strong>Direction Clarity</strong>: Each underlying shows only one direction (CE or PE) based on trend<br>
        • <strong>Risk Management</strong>: Options can expire worthless - only invest what you can afford to lose<br>
        • <strong>Strike Selection</strong>: ATM and slightly OTM strikes for optimal risk-reward<br>
        • <strong>Expiry Awareness</strong>: Monitor time decay, especially in the last week
        </div>
        """, unsafe_allow_html=True)
        
        # Download option
        csv = st.session_state.fno_recos.to_csv(index=False)
        st.download_button(
            "📥 Download F&O Recommendations",
            csv,
            f"fno_options_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv"
        )

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**📊 Professional Trading Dashboard**")
with col2:
    st.markdown(f"**🕐 Last Updated:** {datetime.now().strftime('%H:%M:%S IST')}")
with col3:
    st.markdown(f"**📈 Total Scans Today:** {st.session_state.scan_count}")

# Disclaimer
st.markdown("""
<div style="background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; margin-top: 2rem; font-size: 0.9rem; color: #6c757d;">
<strong>Disclaimer:</strong> This dashboard provides technical analysis based recommendations. Stock market investments are subject to market risks. 
Please consult your financial advisor before making investment decisions. Past performance is not indicative of future results.
</div>
""", unsafe_allow_html=True)
