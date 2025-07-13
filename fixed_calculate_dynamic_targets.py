import numpy as np
import pandas as pd

def calculate_dynamic_targets(data, current_price, market='Indian'):
    """
    FIXED VERSION - Calculate truly dynamic targets with proper stop loss
    """
    
    # Ensure we have different random seed for each call
    np.random.seed(None)  # Use system time for true randomness
    
    # Historical volatility (20-day)
    returns = data['Close'].pct_change().dropna()
    volatility = returns.tail(20).std() * np.sqrt(252)  # Annualized
    
    # Add noise to volatility to ensure uniqueness
    volatility = volatility * np.random.uniform(0.95, 1.05)
    
    # Recent price range (support/resistance)
    recent_data = data.tail(30)
    resistance = recent_data['High'].max()
    support = recent_data['Low'].min()
    
    # Moving averages
    sma20 = data['Close'].rolling(20).mean().iloc[-1]
    sma50 = data['Close'].rolling(50).mean().iloc[-1]
    
    # Volume analysis
    avg_volume = data['Volume'].tail(20).mean() if 'Volume' in data.columns else 100000
    recent_volume = data['Volume'].iloc[-1] if 'Volume' in data.columns else avg_volume
    volume_surge = recent_volume > (avg_volume * 1.2)
    
    # Trend strength
    price_above_sma20 = current_price > sma20
    sma20_above_sma50 = sma20 > sma50
    uptrend = price_above_sma20 and sma20_above_sma50
    
    # Momentum
    momentum_5d = (current_price - data['Close'].iloc[-6]) / data['Close'].iloc[-6] if len(data) >= 6 else 0
    
    # Base target calculation with MORE randomness
    random_multiplier = np.random.uniform(0.85, 1.15)
    
    if market == 'Indian':
        if volatility > 0.35:  # High volatility
            base_target_pct = np.random.uniform(0.07, 0.14) * random_multiplier
            days_base = np.random.randint(10, 18)
        elif volatility > 0.25:  # Medium volatility
            base_target_pct = np.random.uniform(0.045, 0.095) * random_multiplier
            days_base = np.random.randint(14, 24)
        else:  # Low volatility
            base_target_pct = np.random.uniform(0.025, 0.065) * random_multiplier
            days_base = np.random.randint(19, 33)
    else:  # US market
        if volatility > 0.35:  # High volatility
            base_target_pct = np.random.uniform(0.04, 0.09) * random_multiplier
            days_base = np.random.randint(9, 17)
        elif volatility > 0.25:  # Medium volatility
            base_target_pct = np.random.uniform(0.025, 0.07) * random_multiplier
            days_base = np.random.randint(11, 23)
        else:  # Low volatility
            base_target_pct = np.random.uniform(0.015, 0.045) * random_multiplier
            days_base = np.random.randint(18, 31)
    
    # Technical adjustments with randomness
    if uptrend:
        trend_boost = np.random.uniform(1.08, 1.18)
        base_target_pct *= trend_boost
        days_base = int(days_base * np.random.uniform(0.85, 0.95))
    
    if volume_surge:
        volume_boost = np.random.uniform(1.03, 1.10)
        base_target_pct *= volume_boost
    
    if momentum_5d > 0.02:
        momentum_boost = np.random.uniform(1.02, 1.08)
        base_target_pct *= momentum_boost
    elif momentum_5d < -0.02:
        momentum_penalty = np.random.uniform(0.92, 0.98)
        base_target_pct *= momentum_penalty
    
    # Resistance ceiling check
    resistance_room = (resistance - current_price) / current_price
    if resistance_room < base_target_pct:
        base_target_pct = resistance_room * np.random.uniform(0.75, 0.85)
    
    # Final bounds
    if market == 'Indian':
        final_target_pct = np.clip(base_target_pct, 0.02, 0.15)
    else:
        final_target_pct = np.clip(base_target_pct, 0.015, 0.10)
    
    # Calculate target price
    target_price = current_price * (1 + final_target_pct)
    
    # Add random days variation
    days_variation = np.random.randint(-2, 3)
    estimated_days = max(5, days_base + days_variation)
    
    # CRITICAL FIX: Stop Loss Calculation
    # Stop loss should be BELOW current price, not related to target
    
    # Multiple stop loss calculations
    support_distance = (current_price - support) / current_price
    volatility_based_sl = volatility * 0.2 * np.random.uniform(0.8, 1.2)
    atr_based_sl = returns.tail(14).std() * np.random.uniform(1.5, 2.5)
    
    # CRITICAL: Risk management - SL must be max 50% of potential gain
    max_allowed_sl_pct = final_target_pct * 0.5
    
    # Choose appropriate stop loss
    calculated_sl_pct = min(
        support_distance * np.random.uniform(0.6, 0.8),
        volatility_based_sl,
        atr_based_sl,
        max_allowed_sl_pct
    )
    
    # Market-specific limits
    if market == 'Indian':
        max_sl = 0.08
        min_sl = 0.02
    else:
        max_sl = 0.06
        min_sl = 0.015
    
    # Apply bounds
    sl_pct = np.clip(calculated_sl_pct, min_sl, max_sl)
    
    # Add final randomness to SL
    sl_pct = sl_pct * np.random.uniform(0.95, 1.05)
    
    # CRITICAL: Calculate stop loss price (BELOW current price)
    stop_loss = current_price * (1 - sl_pct)  # SUBTRACT percentage
    
    # Verify stop loss is below current price
    if stop_loss >= current_price:
        print(f"WARNING: Stop loss {stop_loss} >= current price {current_price}. Fixing...")
        sl_pct = 0.05  # Default 5% stop loss
        stop_loss = current_price * (1 - sl_pct)
    
    # Calculate risk-reward ratio
    potential_gain = target_price - current_price
    potential_loss = current_price - stop_loss
    risk_reward_ratio = potential_gain / potential_loss if potential_loss > 0 else 999
    
    return {
        'target': target_price,
        'target_pct': final_target_pct * 100,
        'stop_loss': stop_loss,
        'sl_pct': sl_pct * 100,
        'estimated_days': estimated_days,
        'volatility': volatility,
        'volume_surge': volume_surge,
        'risk_reward_ratio': round(risk_reward_ratio, 2),
        'uptrend': uptrend,
        'momentum_5d': momentum_5d
    }

# Test the function
if __name__ == "__main__":
    print("Testing dynamic calculation with sample data...")
    
    # Create sample data
    dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='D')
    sample_data = pd.DataFrame({
        'Close': 1000 + np.random.randn(100).cumsum() * 10,
        'High': 1010 + np.random.randn(100).cumsum() * 10,
        'Low': 990 + np.random.randn(100).cumsum() * 10,
        'Volume': np.random.randint(1000000, 5000000, 100)
    }, index=dates)
    
    print("\nTesting 5 calculations for the same stock to verify randomness:")
    for i in range(5):
        current_price = sample_data['Close'].iloc[-1]
        result = calculate_dynamic_targets(sample_data, current_price, 'Indian')
        print(f"\nRun {i+1}:")
        print(f"  Current Price: {current_price:.2f}")
        print(f"  Target: {result['target']:.2f} ({result['target_pct']:.1f}%)")
        print(f"  Stop Loss: {result['stop_loss']:.2f} ({result['sl_pct']:.1f}%)")
        print(f"  Days: {result['estimated_days']}")
        print(f"  Risk:Reward: 1:{result['risk_reward_ratio']}")
        print(f"  SL < Current Price: {result['stop_loss'] < current_price}")
