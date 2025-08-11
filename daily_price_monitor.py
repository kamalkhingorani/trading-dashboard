import schedule
import time
import threading
from datetime import datetime
import logging
from recommendations_tracker import RecommendationsTracker

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('price_monitor.log'),
        logging.StreamHandler()
    ]
)

class PriceMonitor:
    def __init__(self):
        self.tracker = RecommendationsTracker()
        self.is_running = False
        self.monitor_thread = None
    
    def update_all_prices(self):
        """Update prices for all active recommendations"""
        try:
            logging.info("Starting price update cycle...")
            
            results = self.tracker.update_prices_and_status()
            
            logging.info(f"Price update completed:")
            logging.info(f"  - Updated: {results['updated_count']} stocks")
            logging.info(f"  - Target hits: {results['target_hits']}")
            logging.info(f"  - Stop loss hits: {results['sl_hits']}")
            
            if results['target_hits'] > 0 or results['sl_hits'] > 0:
                logging.info("🎯 ALERT: Some stocks hit targets or stop losses!")
            
            return results
            
        except Exception as e:
            logging.error(f"Error during price update: {e}")
            return None
    
    def start_monitoring(self, update_frequency_minutes=30):
        """Start the automated monitoring process"""
        if self.is_running:
            logging.info("Monitor is already running")
            return
        
        self.is_running = True
        
        # Schedule price updates
        schedule.every(update_frequency_minutes).minutes.do(self.update_all_prices)
        
        # Also schedule a daily summary at 9 AM
        schedule.every().day.at("09:00").do(self.daily_summary)
        
        # Start the monitoring thread
        self.monitor_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.monitor_thread.start()
        
        logging.info(f"Price monitoring started - updating every {update_frequency_minutes} minutes")
    
    def stop_monitoring(self):
        """Stop the automated monitoring"""
        self.is_running = False
        schedule.clear()
        logging.info("Price monitoring stopped")
    
    def _run_scheduler(self):
        """Internal method to run the scheduler"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def daily_summary(self):
        """Generate and log daily summary"""
        try:
            summary = self.tracker.get_performance_summary()
            
            logging.info("📊 DAILY SUMMARY:")
            logging.info(f"  Total Recommendations: {summary['total_recommendations']}")
            logging.info(f"  Active: {summary['active_recommendations']}")
            logging.info(f"  Target Hits: {summary['target_hits']}")
            logging.info(f"  Stop Loss Hits: {summary['sl_hits']}")
            logging.info(f"  Success Rate: {summary['success_rate']}%")
            logging.info(f"  Average Days to Completion: {summary['avg_days_to_completion']}")
            
            if summary['best_performers']:
                logging.info("🏆 Best Performers:")
                for stock, market, return_pct, status, days in summary['best_performers']:
                    logging.info(f"    {stock} ({market}): {return_pct:.1f}% in {days} days")
            
        except Exception as e:
            logging.error(f"Error generating daily summary: {e}")
    
    def force_update_now(self):
        """Force an immediate price update"""
        logging.info("Force updating prices now...")
        return self.update_all_prices()

# Market hours checker
def is_market_hours():
    """Check if it's during market hours (basic implementation)"""
    now = datetime.now()
    
    # Indian market: 9:15 AM to 3:30 PM IST (Mon-Fri)
    # US market: 9:30 AM to 4:00 PM EST (Mon-Fri)
    # For simplicity, we'll update during both market hours
    
    if now.weekday() >= 5:  # Weekend
        return False
    
    hour = now.hour
    # Update between 6 AM to 11 PM to cover both markets
    return 6 <= hour <= 23

class SmartPriceMonitor(PriceMonitor):
    """Enhanced monitor that respects market hours"""
    
    def start_smart_monitoring(self):
        """Start monitoring with market hours awareness"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # More frequent updates during market hours
        schedule.every(15).minutes.do(self._smart_update)
        
        # Daily summary
        schedule.every().day.at("09:00").do(self.daily_summary)
        
        # Remove automatic cleanup - user controls manually
        # schedule.every().sunday.at("23:00").do(self._weekly_cleanup)
        
        self.monitor_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.monitor_thread.start()
        
        logging.info("Smart price monitoring started (no auto-cleanup)")
    
    def _smart_update(self):
        """Update prices only during appropriate times"""
        if is_market_hours():
            return self.update_all_prices()
        else:
            # Light update during off-hours (once every 2 hours)
            if datetime.now().hour % 2 == 0:
                return self.update_all_prices()
    
    def _weekly_cleanup(self):
        """Weekly cleanup of old data"""
        try:
            deleted_count = self.tracker.cleanup_old_recommendations(days_old=90)
            logging.info(f"Weekly cleanup: Removed {deleted_count} old recommendations")
        except Exception as e:
            logging.error(f"Error during weekly cleanup: {e}")

# Global monitor instance
price_monitor = SmartPriceMonitor()

def start_background_monitoring():
    """Start the background monitoring service"""
    price_monitor.start_smart_monitoring()

def stop_background_monitoring():
    """Stop the background monitoring service"""
    price_monitor.stop_monitoring()

def force_price_update():
    """Force an immediate price update"""
    return price_monitor.force_update_now()

def get_monitoring_status():
    """Get current monitoring status"""
    return {
        'is_running': price_monitor.is_running,
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

if __name__ == "__main__":
    # For testing - run the monitor
    print("Starting price monitor for testing...")
    monitor = SmartPriceMonitor()
    monitor.start_smart_monitoring()
    
    # Keep running
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Stopping monitor...")
        monitor.stop_monitoring()
