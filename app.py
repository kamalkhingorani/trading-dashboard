# final_app.py - LOCAL DATABASE WITH IMMEDIATE APPEND
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import time

# Import the local tracking system
try:
    from local_recommendations_tracker import LocalRecommendationsTracker
    TRACKING_AVAILABLE = True
    # Initialize tracker immediately
    if 'tracker' not in st.session_state:
        st.session_state.tracker = LocalRecommendationsTracker()
        st.success(f"✅ Local database ready at: {st.session_state.tracker.db_path}")
except ImportError:
    TRACKING_AVAILABLE = False
    st.error("❌ Local tracking system not available. Please ensure local_recommendations_tracker.py is in the same directory.")

# Safe import handling for stock logic
@st.cache_data
def safe_import_modules():
    """Safely import custom modules with fallback options"""
    modules = {}
    
    try:
        from indian_stock_logic import get_indian_recommendations, get_indian_market_overview
        modules['indian_stock'] = True
        modules['get_indian_recommendations'] = get_indian_recommendations
        modules['get_indian_market_overview'] = get_indian_market_overview
        st.success("✅ Indian stock logic imported successfully")
    except Exception as e:
        modules['indian_stock'] = False
        st.error(f"❌ Indian stock logic import failed: {e}")
    
    try:
        from us_stock_logic import get_us_recommendations, get_us_market_overview
        modules['us_stock'] = True
        modules['get_us_recommendations'] = get_us_recommendations
        modules['get_us_market_overview'] = get_us_market_overview
        st.success("✅ US stock logic imported successfully")
    except Exception as e:
        modules['us_stock'] = False
        st.error(f"❌ US stock logic import failed: {e}")
    
    try:
        from fixed_fno_options_logic import generate_fno_opportunities, get_options_summary
        modules['fno'] = True
        modules['generate_fno_opportunities'] = generate_fno_opportunities
        modules['get_options_summary'] = get_options_summary
        st.success("✅ F&O options logic imported successfully")
    except Exception as e:
        modules['fno'] = False
        st.error(f"❌ F&O options logic import failed: {e}")
    
    try:
        from news_logic import get_latest_news
        modules['news'] = True
        modules['get_latest_news'] = get_latest_news
        st.success("✅ News logic imported successfully")
    except Exception as e:
        modules['news'] = False
        st.error(f"❌ News logic import failed: {e}")
    
    return modules

# Page configuration
st.set_page_config(
    page_title="Kamal's Local Trading Dashboard",
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
    .db-info {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .performance-metric {
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 0.3rem;
        text-align: center;
        margin: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for recommendations
if 'indian_recos' not in st.session_state:
    st.session_state.indian_recos = pd.DataFrame()
if 'us_recos' not in st.session_state:
    st.session_state.us_recos = pd.DataFrame()
if 'fno_recos' not in st.session_state:
    st.session_state.fno_recos = pd.DataFrame()
if 'news_data' not in st.session_state:
    st.session_state.news_data = []

# Main title
st.markdown('<h1 class="main-header">📈 Kamal\'s Local Auto-Append Trading Dashboard</h1>', unsafe_allow_html=True)

# Import modules
modules = safe_import_modules()

# Database Information
if TRACKING_AVAILABLE:
    db_info = st.session_state.tracker.get_database_info()
    st.markdown(f"""
    <div class="db-info">
    <strong>💾 Local Database Status</strong><br>
    📁 Path: {db_info['path']}<br>
    📊 Records: {db_info.get('total_records', 0)}<br>
    💿 Size: {db_info.get('size_kb', 0)} KB<br>
    ✅ Auto-append: ACTIVE (Every scan adds to database immediately)
    </div>
    """, unsafe_allow_html=True)
    
    # Performance Dashboard
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Update All Prices Now"):
            with st.spinner("Updating prices from market..."):
                results = st.session_state.tracker.update_prices_and_status()
                if results:
                    st.success(f"✅ Updated {results['updated_count']} prices | 🎯 Targets: {results['target_hits']} | 🛑 SL: {results['sl_hits']}")
    
    with col2:
        if st.button("📊 View Performance Summary"):
            summary = st.session_state.tracker.get_performance_summary()
            
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.markdown(f"""
                <div class="performance-metric">
                <h4>{summary['total_recommendations']}</h4>
                <small>Total Recommendations</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col_b:
                st.markdown(f"""
                <div class="performance-metric">
                <h4>{summary['active_recommendations']}</h4>
                <small>Active Trades</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col_c:
                st.markdown(f"""
                <div class="performance-metric">
                <h4>{summary['success_rate']}%</h4>
                <small>Success Rate</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col_d:
                st.markdown(f"""
                <div class="performance-metric">
                <h4>{summary['avg_return']}%</h4>
                <small>Avg Return</small>
                </div>
                """, unsafe_allow_html=True)
    
    with col3:
        if st.button("📁 Export Database"):
            filename = st.session_state.tracker.export_to_csv()
            st.success(f"✅ Exported to: {filename}")

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📰 Market News", "🇮🇳 Indian Stocks", "🇺🇸 US Stocks", "📊 F&O Options", "📋 Database View"])

# Tab 1: Market News
with tab1:
    st.subheader("📰 Latest Market News & Analysis")
    
    if st.button("🔄 Refresh News", type="primary"):
        if modules.get('news'):
            try:
                st.session_state.news_data = modules['get_latest_news']()
                if st.session_state.news_data:
                    st.success(f"✅ Loaded {len(st.session_state.news_data)} latest news items")
            except Exception as e:
                st.error(f"Error loading news: {e}")
    
    if st.session_state.news_data:
        for news in st.session_state.news_data:
            with st.container():
                st.markdown(f"""
                **{news.get('title', 'No Title')}**  
                {news.get('summary', 'No summary available')}  
                📊 **{news.get('category', 'General')}** | 🎯 **{news.get('market_impact', 'Low')}** Impact | 🕒 {news.get('time', 'Unknown')} IST
                """)
                st.markdown("---")

# Tab 2: Indian Stocks
with tab2:
    st.subheader("🇮🇳 Indian Stock Recommendations - Auto-Append to Database")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        min_price_in = st.number_input("Min Price (₹)", value=25, min_value=1, key="in_price")
    with col2:
        max_rsi_in = st.number_input("Max RSI", value=70, min_value=1, max_value=100, key="in_rsi")
    with col3:
        batch_size_in = st.number_input("Stocks to Scan", value=200, min_value=50, max_value=500, key="in_batch")
    
    if st.button("🔍 Scan Indian Stocks", type="primary"):
        with st.spinner("Scanning Indian stocks..."):
            try:
                if modules.get('indian_stock'):
                    st.session_state.indian_recos = modules['get_indian_recommendations'](
                        min_price_in, max_rsi_in, min_volume=50000, batch_size=batch_size_in
                    )
                    
                    if not st.session_state.indian_recos.empty:
                        st.success(f"🎯 Found {len(st.session_state.indian_recos)} Indian stock opportunities!")
                        
                        # IMMEDIATE AUTO-APPEND TO DATABASE
                        if TRACKING_AVAILABLE:
                            added_count = st.session_state.tracker.add_recommendations(
                                st.session_state.indian_recos, "Indian"
                            )
                            st.markdown(f"""
                            <div class="db-info">
                            <strong>💾 AUTO-APPENDED TO DATABASE!</strong><br>
                            ✅ Added {added_count} new Indian stocks to local database<br>
                            📁 Location: C:\\Users\\kamal\\Downloads\\DASHBOARD FILES\\recommendations_tracker.db<br>
                            🔄 Previous data preserved, new data appended
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.warning("No stocks found. Try relaxing the criteria.")
                else:
                    st.error("Indian stock module not available")
            except Exception as e:
                st.error(f"Error during scan: {e}")
    
    if not st.session_state.indian_recos.empty:
        st.markdown(f"**📊 Latest Scan Results: {len(st.session_state.indian_recos)} opportunities**")
        
        # Copy functionality
        col1, col2 = st.columns(2)
        with col1:
            copy_text = st.session_state.us_recos.to_string(index=False, max_cols=None, max_rows=None)
            st.text_area("📋 Copy Exact Format (Select All + Ctrl+C):", copy_text, height=150, key="copy_us_exact")
        
        with col2:
            copy_tsv = st.session_state.us_recos.to_csv(index=False, sep='\t')
            st.text_area("📋 Copy for Excel (Tab-separated):", copy_tsv, height=150, key="copy_us_excel")
        
        st.dataframe(
            st.session_state.us_recos, 
            use_container_width=True, 
            height=400,
            column_config={
                "Selection Reason": st.column_config.TextColumn(width="large")
            }
        )

# Tab 4: F&O Options
with tab4:
    st.subheader("📊 F&O Options & Index Trading")
    
    if modules.get('fno'):
        if st.button("🔍 Generate F&O Opportunities", type="primary"):
            with st.spinner("Generating F&O analysis..."):
                try:
                    st.session_state.fno_recos = modules['generate_fno_opportunities']()
                    
                    if not st.session_state.fno_recos.empty:
                        summary = modules['get_options_summary'](st.session_state.fno_recos)
                        st.success(f"🎯 Generated {summary['total_opportunities']} F&O opportunities!")
                    else:
                        st.warning("No F&O opportunities found.")
                except Exception as e:
                    st.error(f"Error generating F&O opportunities: {e}")
        
        if not st.session_state.fno_recos.empty:
            st.markdown(f"**📊 F&O Results: {len(st.session_state.fno_recos)} opportunities**")
            st.dataframe(st.session_state.fno_recos, use_container_width=True, height=500)
            
            # Download option
            csv = st.session_state.fno_recos.to_csv(index=False)
            st.download_button(
                "📥 Download F&O Recommendations",
                csv,
                f"fno_opportunities_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv"
            )
    else:
        st.error("F&O module not available")

# Tab 5: Database View
with tab5:
    st.subheader("📋 Complete Database View - All Historical Recommendations")
    
    if TRACKING_AVAILABLE:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "Active", "Target Hit", "SL Hit", "Archived"],
                key="status_filter"
            )
        
        with col2:
            market_filter = st.selectbox(
                "Filter by Market", 
                ["All", "Indian", "US"],
                key="market_filter"
            )
        
        with col3:
            if st.button("🗂️ Archive Completed"):
                archived_count = st.session_state.tracker.archive_completed_recommendations()
                st.success(f"✅ Archived {archived_count} completed recommendations")
                st.rerun()
        
        with col4:
            if st.button("🔄 Refresh Data"):
                st.rerun()
        
        # Manual cleanup section
        st.markdown("### 🗑️ Manual Data Management")
        col_a, col_b = st.columns(2)
        
        with col_a:
            days_old = st.number_input("Delete records older than (days):", value=180, min_value=30, max_value=365)
            if st.button("🗑️ Delete Old Records", help="Only deletes Target Hit/SL Hit/Archived records"):
                deleted_count = st.session_state.tracker.manual_cleanup_old_records(days_old)
                st.success(f"✅ Deleted {deleted_count} old records")
                st.rerun()
        
        with col_b:
            st.markdown("**Individual Delete:**")
            delete_id = st.number_input("Enter ID to delete:", min_value=1, step=1)
            if st.button("🗑️ Delete by ID"):
                if st.session_state.tracker.delete_recommendation(delete_id):
                    st.success(f"✅ Deleted recommendation ID: {delete_id}")
                    st.rerun()
                else:
                    st.error(f"❌ Could not find recommendation ID: {delete_id}")
        
        # Get and display filtered data
        all_recommendations = st.session_state.tracker.get_all_recommendations(status_filter, market_filter)
        
        if not all_recommendations.empty:
            st.markdown(f"**📊 Showing {len(all_recommendations)} recommendations**")
            
            # Display key columns
            display_columns = [
                'id', 'date_added', 'market', 'stock_symbol', 'entry_price', 'current_price', 
                'target_price', 'stop_loss', 'current_return_pct', 'status', 'days_elapsed',
                'target_hit_date', 'sl_hit_date', 'sector', 'selection_reason', 'last_updated'
            ]
            
            # Filter columns that exist
            existing_columns = [col for col in display_columns if col in all_recommendations.columns]
            
            st.dataframe(
                all_recommendations[existing_columns],
                use_container_width=True,
                height=600,
                column_config={
                    "selection_reason": st.column_config.TextColumn(width="large"),
                    "current_return_pct": st.column_config.NumberColumn(
                        "Current Return %",
                        format="%.2f%%"
                    ),
                    "id": st.column_config.NumberColumn("ID", width="small")
                }
            )
            
            # Export filtered data
            csv_filtered = all_recommendations.to_csv(index=False)
            st.download_button(
                "📥 Export Filtered Data",
                csv_filtered,
                f"filtered_recommendations_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv"
            )
            
        else:
            st.info("No recommendations found matching the selected filters.")
    
    else:
        st.error("Database tracking not available")

# Sidebar
st.sidebar.title("💾 Local Database Info")

if TRACKING_AVAILABLE:
    db_info = st.session_state.tracker.get_database_info()
    summary = st.session_state.tracker.get_performance_summary()
    
    st.sidebar.success("✅ Database Active")
    st.sidebar.metric("Total Records", summary['total_recommendations'])
    st.sidebar.metric("Active Trades", summary['active_recommendations'])
    st.sidebar.metric("Success Rate", f"{summary['success_rate']}%")
    st.sidebar.metric("Database Size", f"{db_info.get('size_kb', 0)} KB")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**💾 Database Location:**")
    st.sidebar.code(db_info['path'])
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🔧 Features:**")
    st.sidebar.markdown("• Instant scan append")
    st.sidebar.markdown("• Manual price updates")
    st.sidebar.markdown("• Target/SL detection")
    st.sidebar.markdown("• Manual data management")
    st.sidebar.markdown("• Copy/paste functionality")
    st.sidebar.markdown("• Local file storage")
    
else:
    st.sidebar.error("❌ Database Unavailable")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
<strong>Kamal's Local Auto-Append Trading Dashboard</strong><br>
💾 Local database storage • 🔄 Immediate append • 📊 Manual control<br>
<em>Every scan automatically saves to: C:\\Users\\kamal\\Downloads\\DASHBOARD FILES\\</em>
</div>
""", unsafe_allow_html=True).indian_recos.to_string(index=False, max_cols=None, max_rows=None)
     st.text_area("📋 Copy Exact Format (Select All + Ctrl+C):", copy_text, height=150, key="copy_indian_exact")
        
        with col2:
            copy_tsv = st.session_state.indian_recos.to_csv(index=False, sep='\t')
            st.text_area("📋 Copy for Excel (Tab-separated):", copy_tsv, height=150, key="copy_indian_excel")
        
        st.dataframe(
            st.session_state.indian_recos, 
            use_container_width=True, 
            height=400,
            column_config={
                "Selection Reason": st.column_config.TextColumn(width="large")
            }
        )

# Tab 3: US Stocks
with tab3:
    st.subheader("🇺🇸 US Stock Recommendations - Auto-Append to Database")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        min_price_us = st.number_input("Min Price ($)", value=25, min_value=1, key="us_price")
    with col2:
        max_rsi_us = st.number_input("Max RSI", value=65, min_value=1, max_value=100, key="us_rsi")
    with col3:
        batch_size_us = st.number_input("Stocks to Scan", value=200, min_value=50, max_value=500, key="us_batch")
    
    if st.button("🔍 Scan US Stocks", type="primary"):
        with st.spinner("Scanning US stocks..."):
            try:
                if modules.get('us_stock'):
                    st.session_state.us_recos = modules['get_us_recommendations'](
                        min_price_us, max_rsi_us, min_volume=500000, batch_size=batch_size_us
                    )
                    
                    if not st.session_state.us_recos.empty:
                        st.success(f"🎯 Found {len(st.session_state.us_recos)} US stock opportunities!")
                        
                        # IMMEDIATE AUTO-APPEND TO DATABASE
                        if TRACKING_AVAILABLE:
                            added_count = st.session_state.tracker.add_recommendations(
                                st.session_state.us_recos, "US"
                            )
                            st.markdown(f"""
                            <div class="db-info">
                            <strong>💾 AUTO-APPENDED TO DATABASE!</strong><br>
                            ✅ Added {added_count} new US stocks to local database<br>
                            📁 Location: C:\\Users\\kamal\\Downloads\\DASHBOARD FILES\\recommendations_tracker.db<br>
                            🔄 Previous data preserved, new data appended
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.warning("No stocks found. Try relaxing the criteria.")
                else:
                    st.error("US stock module not available")
            except Exception as e:
                st.error(f"Error during scan: {e}")
    
    if not st.session_state.us_recos.empty:
        st.markdown(f"**📊 Latest Scan Results: {len(st.session_state.us_recos)} opportunities**")
        
        # Copy functionality
        col1, col2 = st.columns(2)
        with col1:
            copy_text = st.session_state
