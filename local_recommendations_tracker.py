import sqlite3
import pandas as pd
from datetime import datetime
import yfinance as yf
import os

class LocalRecommendationsTracker:
    def __init__(self):
        # HARDCODED PATH - Your Downloads/DASHBOARD FILES directory
        self.db_directory = r"C:\Users\kamal\Downloads\DASHBOARD FILES"
        self.db_path = os.path.join(self.db_directory, "recommendations_tracker.db")
        
        # Ensure directory exists
        os.makedirs(self.db_directory, exist_ok=True)
        
        # Initialize database
        self.init_database()
        print(f"✅ Database initialized at: {self.db_path}")
    
    def init_database(self):
        """Initialize the SQLite database with recommendations table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_added TEXT NOT NULL,
                scan_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                market TEXT NOT NULL,
                stock_symbol TEXT NOT NULL,
                entry_price REAL NOT NULL,
                target_price REAL NOT NULL,
                stop_loss REAL NOT NULL,
                target_pct REAL NOT NULL,
                sl_pct REAL NOT NULL,
                estimated_days INTEGER,
                rsi_value TEXT,
                selection_reason TEXT,
                sector TEXT,
                risk_level TEXT,
                tech_score TEXT,
                volatility TEXT,
                weekly_status TEXT,
                status TEXT DEFAULT 'Active',
                current_price REAL,
                last_updated TEXT,
                target_hit_date TEXT,
                sl_hit_date TEXT,
                max_price_achieved REAL,
                min_price_achieved REAL,
                days_elapsed INTEGER DEFAULT 0,
                current_return_pct REAL DEFAULT 0.0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_recommendations(self, recommendations_df, market):
        """APPEND new recommendations to existing database (no overwrite)"""
        if recommendations_df.empty:
            print(f"⚠️ No {market} recommendations to add")
            return 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        added_count = 0
        duplicate_count = 0
        
        for _, row in recommendations_df.iterrows():
            # Check if this exact stock from same date is already in database
            cursor.execute('''
                SELECT COUNT(*) FROM recommendations 
                WHERE stock_symbol = ? AND market = ? AND date_added = ? AND status = 'Active'
            ''', (row['Stock'], market, row['Date']))
            
            existing_count = cursor.fetchone()[0]
            
            if existing_count == 0:  # Only add if not duplicate from same scan date
                cursor.execute('''
                    INSERT INTO recommendations (
                        date_added, market, stock_symbol, entry_price, target_price, 
                        stop_loss, target_pct, sl_pct, estimated_days, rsi_value,
                        selection_reason, sector, risk_level, tech_score, volatility, weekly_status,
                        current_price, last_updated, max_price_achieved, min_price_achieved
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['Date'],
                    market,
                    row['Stock'],
                    row['LTP'],
                    row['Target'],
                    row['Stop Loss'],
                    row['% Gain'],
                    row['SL %'],
                    row.get('Est.Days', 0),
                    str(row['RSI']),
                    row.get('Selection Reason', ''),
                    row.get('Sector', ''),
                    row.get('Risk', ''),
                    row.get('Tech Score', ''),
                    row.get('Volatility', ''),
                    row.get('Weekly Status', ''),
                    row['LTP'],  # current_price starts as entry_price
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    row['LTP'],  # max_price starts as entry_price
                    row['LTP']   # min_price starts as entry_price
                ))
                added_count += 1
            else:
                duplicate_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"✅ Added {added_count} new {market} recommendations to database")
        if duplicate_count > 0:
            print(f"⚠️ Skipped {duplicate_count} duplicates from same scan date")
        
        return added_count
    
    def update_prices_and_status(self):
        """Update current prices and check for target/SL hits"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all active recommendations
        cursor.execute("SELECT * FROM recommendations WHERE status = 'Active'")
        active_recommendations = cursor.fetchall()
        
        updated_count = 0
        target_hits = 0
        sl_hits = 0
        
        print(f"🔄 Updating prices for {len(active_recommendations)} active recommendations...")
        
        for rec in active_recommendations:
            id_val = rec[0]
            market = rec[3]
            symbol = rec[4]
            entry_price = rec[5]
            target_price = rec[6]
            stop_loss = rec[7]
            max_price = rec[23] if rec[23] else entry_price
            min_price = rec[24] if rec[24] else entry_price
            
            try:
                # Add market suffix for Indian stocks
                ticker_symbol = f"{symbol}.NS" if market == "Indian" else symbol
                
                # Fetch current price
                stock = yf.Ticker(ticker_symbol)
                data = stock.history(period="1d")
                
                if not data.empty:
                    new_current_price = float(data['Close'].iloc[-1])
                    
                    # Update max/min prices achieved
                    new_max_price = max(max_price, new_current_price)
                    new_min_price = min(min_price, new_current_price)
                    
                    # Calculate days elapsed
                    date_added = rec[1]  # date_added column
                    try:
                        date_added_dt = datetime.strptime(date_added, '%Y-%m-%d')
                        days_elapsed = (datetime.now() - date_added_dt).days
                    except:
                        days_elapsed = 0
                    
                    # Calculate current return percentage
                    current_return_pct = ((new_current_price - entry_price) / entry_price) * 100
                    
                    # Check for target hit
                    if new_current_price >= target_price:
                        cursor.execute('''
                            UPDATE recommendations SET 
                            status = 'Target Hit', current_price = ?, last_updated = ?, 
                            target_hit_date = ?, max_price_achieved = ?, min_price_achieved = ?,
                            days_elapsed = ?, current_return_pct = ?
                            WHERE id = ?
                        ''', (
                            new_current_price,
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            datetime.now().strftime('%Y-%m-%d'),
                            new_max_price,
                            new_min_price,
                            days_elapsed,
                            round(current_return_pct, 2),
                            id_val
                        ))
                        target_hits += 1
                        print(f"🎯 TARGET HIT: {symbol} at ₹{new_current_price:.2f}")
                    
                    # Check for stop loss hit
                    elif new_current_price <= stop_loss:
                        cursor.execute('''
                            UPDATE recommendations SET 
                            status = 'SL Hit', current_price = ?, last_updated = ?, 
                            sl_hit_date = ?, max_price_achieved = ?, min_price_achieved = ?,
                            days_elapsed = ?, current_return_pct = ?
                            WHERE id = ?
                        ''', (
                            new_current_price,
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            datetime.now().strftime('%Y-%m-%d'),
                            new_max_price,
                            new_min_price,
                            days_elapsed,
                            round(current_return_pct, 2),
                            id_val
                        ))
                        sl_hits += 1
                        print(f"🛑 STOP LOSS HIT: {symbol} at ₹{new_current_price:.2f}")
                    
                    # Update price for active stocks
                    else:
                        cursor.execute('''
                            UPDATE recommendations SET 
                            current_price = ?, last_updated = ?, 
                            max_price_achieved = ?, min_price_achieved = ?,
                            days_elapsed = ?, current_return_pct = ?
                            WHERE id = ?
                        ''', (
                            new_current_price,
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            new_max_price,
                            new_min_price,
                            days_elapsed,
                            round(current_return_pct, 2),
                            id_val
                        ))
                    
                    updated_count += 1
                    
            except Exception as e:
                print(f"❌ Error updating {symbol}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        print(f"✅ Updated {updated_count} prices | Targets: {target_hits} | SL: {sl_hits}")
        
        return {
            'updated_count': updated_count,
            'target_hits': target_hits,
            'sl_hits': sl_hits
        }
    
    def get_all_recommendations(self, status_filter=None, market_filter=None):
        """Get all recommendations with optional filters"""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM recommendations"
        conditions = []
        params = []
        
        if status_filter and status_filter != "All":
            conditions.append("status = ?")
            params.append(status_filter)
        
        if market_filter and market_filter != "All":
            conditions.append("market = ?")
            params.append(market_filter)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY scan_timestamp DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df
    
    def get_performance_summary(self):
        """Get performance summary statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Overall stats
        cursor.execute("SELECT COUNT(*) FROM recommendations")
        total_recommendations = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM recommendations WHERE status = 'Active'")
        active_recommendations = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM recommendations WHERE status = 'Target Hit'")
        target_hits = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM recommendations WHERE status = 'SL Hit'")
        sl_hits = cursor.fetchone()[0]
        
        # Calculate success rate
        completed = target_hits + sl_hits
        success_rate = (target_hits / completed * 100) if completed > 0 else 0
        
        # Average days to completion
        cursor.execute("SELECT AVG(days_elapsed) FROM recommendations WHERE status IN ('Target Hit', 'SL Hit')")
        avg_days_to_completion = cursor.fetchone()[0] or 0
        
        # Average return for completed trades
        cursor.execute("SELECT AVG(current_return_pct) FROM recommendations WHERE status IN ('Target Hit', 'SL Hit')")
        avg_return = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_recommendations': total_recommendations,
            'active_recommendations': active_recommendations,
            'target_hits': target_hits,
            'sl_hits': sl_hits,
            'success_rate': round(success_rate, 1),
            'avg_days_to_completion': round(avg_days_to_completion, 1),
            'avg_return': round(avg_return, 2)
        }
    
    def delete_recommendation(self, recommendation_id):
        """Delete a specific recommendation by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM recommendations WHERE id = ?", (recommendation_id,))
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return deleted_count > 0
    
    def archive_completed_recommendations(self):
        """Move completed recommendations to archive status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE recommendations SET status = 'Archived' 
            WHERE status IN ('Target Hit', 'SL Hit')
        ''')
        
        archived_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return archived_count
    
    def manual_cleanup_old_records(self, days_old):
        """Manual cleanup of old records (user-controlled only)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM recommendations 
            WHERE status IN ('Archived', 'Target Hit', 'SL Hit')
            AND date(scan_timestamp) < date('now', '-{} days')
        '''.format(days_old))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count
    
    def export_to_csv(self, filename=None):
        """Export all recommendations to CSV"""
        if filename is None:
            filename = os.path.join(self.db_directory, f"recommendations_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        
        df = self.get_all_recommendations()
        df.to_csv(filename, index=False)
        return filename
    
    def get_database_info(self):
        """Get database file information"""
        try:
            file_size = os.path.getsize(self.db_path) / 1024  # Size in KB
            file_exists = os.path.exists(self.db_path)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM recommendations")
            total_records = cursor.fetchone()[0]
            conn.close()
            
            return {
                'path': self.db_path,
                'exists': file_exists,
                'size_kb': round(file_size, 2),
                'total_records': total_records
            }
        except Exception as e:
            return {
                'path': self.db_path,
                'exists': False,
                'error': str(e)
            }
