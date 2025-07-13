import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# Test the dynamic calculation logic directly
def test_dynamic_targets():
    """Test if dynamic targets are actually different for different stocks"""
    
    print("Testing Dynamic Target Calculation...")
    print("=" * 60)
    
    test_stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ITC.NS"]
    results = []
    
    for symbol in test_stocks:
        try:
            print(f"\nAnalyzing {symbol}...")
            stock = yf.Ticker(symbol)
            data = stock.history(period="6mo", interval="1d")
            
            if len(data) < 50:
                print(f"  ⚠️  Insufficient data for {symbol}")
                continue
            
            current_price = data['Close'].iloc[-1]
            
            # Calculate volatility
            returns = data['Close'].pct_change().dropna()
            volatility = returns.tail(20).std() * np.sqrt(252)
            
            # Recent price range
            recent_data = data.tail(30)
            resistance = recent_data['High'].max()
            support = recent_data['Low'].min()
            
            # Calculate target with randomness
            if volatility > 0.35:
                base_target_pct = np.random.uniform(0.08, 0.15)
                days_range = (10, 20)
            elif volatility > 0.25:
                base_target_pct = np.random.uniform(0.05, 0.10)
                days_range = (15, 25)
            else:
                base_target_pct = np.random.uniform(0.03, 0.07)
                days_range = (20, 35)
            
            # Add random factor
            random_factor = np.random.uniform(0.9, 1.1)
            final_target_pct = base_target_pct * random_factor
            
            target_price = current_price * (1 + final_target_pct)
            estimated_days = np.random.randint(days_range[0], days_range[1])
            
            # Calculate stop loss (should be BELOW current price)
            sl_pct = min(final_target_pct * 0.5, 0.08)  # Max 50% of gain or 8%
            sl_pct = max(sl_pct, 0.02)  # Min 2%
            stop_loss = current_price * (1 - sl_pct)  # SUBTRACT from current price
            
            # Risk-reward calculation
            potential_gain = target_price - current_price
            potential_loss = current_price - stop_loss
            risk_reward = potential_gain / potential_loss if potential_loss > 0 else 0
            
            result = {
                'Stock': symbol,
                'Current Price': round(current_price, 2),
                'Target': round(target_price, 2),
                'Target %': round(final_target_pct * 100, 1),
                'Stop Loss': round(stop_loss, 2),
                'SL %': round(sl_pct * 100, 1),
                'Days': estimated_days,
                'Risk:Reward': round(risk_reward, 2),
                'Volatility': round(volatility, 3)
            }
            
            results.append(result)
            
            print(f"  Current: ₹{current_price:.2f}")
            print(f"  Target: ₹{target_price:.2f} ({final_target_pct*100:.1f}%)")
            print(f"  Stop Loss: ₹{stop_loss:.2f} ({sl_pct*100:.1f}%)")
            print(f"  Days: {estimated_days}")
            print(f"  Risk:Reward: 1:{risk_reward:.1f}")
            print(f"  Volatility: {volatility:.3f}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Display results as dataframe
    if results:
        df = pd.DataFrame(results)
        print("\n" + "=" * 60)
        print("SUMMARY OF RESULTS:")
        print("=" * 60)
        print(df.to_string(index=False))
        
        # Check if values are different
        print("\n" + "=" * 60)
        print("VERIFICATION:")
        print(f"Unique Target %: {df['Target %'].nunique()} (should be {len(df)})")
        print(f"Unique Days: {df['Days'].nunique()} (should be close to {len(df)})")
        print(f"Unique SL %: {df['SL %'].nunique()} (should be multiple values)")
        print(f"All Stop Losses < Current Prices: {all(df['Stop Loss'] < df['Current Price'])}")
        print(f"All Risk:Reward >= 2.0: {all(df['Risk:Reward'] >= 2.0)}")
    
    return results

# Run the test
if __name__ == "__main__":
    test_dynamic_targets()
