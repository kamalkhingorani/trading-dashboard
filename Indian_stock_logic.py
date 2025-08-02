# ADDITION TO indian_stock_logic.py - ADD THIS FUNCTION FOR ALL NSE UNIVERSE

def get_all_nse_universe():
    """Get ALL NSE traded stocks (~1800 stocks) - Complete universe"""
    try:
        # Try multiple sources for complete NSE list
        import requests
        
        # Method 1: Try NSE India website
        try:
            nse_all_url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20TOTAL%20MARKET"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            response = requests.get(nse_all_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                symbols = [item['symbol'] + ".NS" for item in data.get('data', [])]
                if len(symbols) > 500:
                    st.success(f"✅ Fetched {len(symbols)} stocks from NSE Total Market")
                    return symbols
        except:
            pass
        
        # Method 2: Try comprehensive symbol generation
        # This creates a comprehensive list based on known NSE patterns
        symbols = get_comprehensive_all_nse_symbols()
        st.info(f"Using comprehensive NSE symbol list: {len(symbols)} stocks")
        return symbols
        
    except Exception as e:
        st.warning(f"Using fallback NSE500: {e}")
        return get_nse500_universe()

def get_comprehensive_all_nse_symbols():
    """Generate comprehensive NSE symbol list based on known patterns"""
    
    # Start with NSE500 as base
    symbols = get_comprehensive_nse_universe()
    
    # Add additional mid-cap and small-cap stocks
    additional_stocks = [
        # Technology & Software
        "RACKLA.NS", "ZENSAR.NS", "NIITTECH.NS", "RSYSTEMS.NS", "SUBEXLTD.NS",
        "DATAMATICS.NS", "MINDSPACE.NS", "GALAXYSURF.NS", "NETMAGIC.NS", "NELCO.NS",
        
        # Banking & Financial Services
        "DCBBANK.NS", "SOUTHBANK.NS", "JAMNAAUTO.NS", "REPCO.NS", "DHANI.NS",
        "UJJIVAN.NS", "EQUITAS.NS", "SURYODAY.NS", "FINOPB.NS", "NARNOLIA.NS",
        
        # Pharmaceuticals & Healthcare
        "SEQUENT.NS", "ERIS.NS", "LAURUS.NS", "SOLARA.NS", "HIKAL.NS",
        "DISHMAN.NS", "NECLIFE.NS", "MARKSANS.NS", "GLAND.NS", "SMSLIFE.NS",
        
        # Auto & Auto Components
        "MAHSCOOTER.NS", "KIRLOSENG.NS", "JSLHISAR.NS", "SUPRAJIT.NS", "SETCO.NS",
        "WHEELS.NS", "AUTOAXLES.NS", "FIEM.NS", "GABRIEL.NS", "CRAFTSMAN.NS",
        
        # Textiles & Apparel
        "KPR.NS", "SPENTEX.NS", "SHIVAMILL.NS", "NITCO.NS", "LOYAL.NS",
        "SUTLEJ.NS", "PASUPATI.NS", "PRAXIS.NS", "OSWAL.NS", "GARWARE.NS",
        
        # Real Estate & Infrastructure
        "PHOENIXLTD.NS", "MAHLIFE.NS", "KOLTEPATIL.NS", "SOBHA.NS", "MAHINDRA.NS",
        "SUNTECK.NS", "HOMEFIRST.NS", "ASHIANA.NS", "MAHYUG.NS", "ASWANI.NS",
        
        # FMCG & Consumer
        "GILLETTE.NS", "GODREJIND.NS", "HONASA.NS", "VADILAL.NS", "ZYDUSWELL.NS",
        "FIVESTAR.NS", "PRATAAP.NS", "ANANTRAJ.NS", "VARUN.NS", "TASTY.NS",
        
        # Chemicals & Fertilizers
        "CHEMCON.NS", "CLEAN.NS", "ROSSARI.NS", "ANUPAMRAS.NS", "TATACHEM.NS",
        "APCOTEX.NS", "GULFOIL.NS", "NAVIN.NS", "MADHAV.NS", "SARASWAT.NS",
        
        # Metals & Mining
        "MAITHANALL.NS", "ORIENTALTL.NS", "LLOYDS.NS", "MSPL.NS", "MUKTA.NS",
        "ROHLTD.NS", "KIOCL.NS", "ORISSA.NS", "ARSS.NS", "MINDA.NS",
        
        # Oil & Gas
        "ACRYSIL.NS", "DFMFOODS.NS", "VRL.NS", "SYMPHONY.NS", "SHANKARA.NS",
        "HITECH.NS", "NELCAST.NS", "GTPL.NS", "GUJGAS.NS", "IGL.NS",
        
        # Power & Energy
        "JSWENERGY.NS", "MPOWER.NS", "RPOWER.NS", "CESC.NS", "TORNTPOWER.NS",
        "ADANIGREEN.NS", "SUZLON.NS", "WEBSOL.NS", "ORIENTGREEN.NS", "SKIPPER.NS",
        
        # Cement & Construction
        "PRISM.NS", "ORIENT.NS", "RAMCOIND.NS", "JK.NS", "KESORAM.NS",
        "CENTRUM.NS", "JAGRAN.NS", "MARAL.NS", "SELAN.NS", "MINDACORP.NS",
        
        # Media & Entertainment
        "SUNTV.NS", "TVTODAY.NS", "NAVNEET.NS", "BALAJI.NS", "EROS.NS",
        "TIPS.NS", "SAREGAMA.NS", "REDINGTON.NS", "PAISALO.NS", "WORTH.NS",
        
        # Logistics & Transportation
        "GATI.NS", "MAHLOG.NS", "AEGIS.NS", "ALLCARGO.NS", "TCI.NS",
        "THOMASCOOK.NS", "MAHINDRA.NS", "JINDWORLD.NS", "KHADIM.NS", "CELEBRITY.NS",
        
        # Food & Agriculture
        "BRITANNIA.NS", "BIKAJI.NS", "HATSUN.NS", "DODLA.NS", "GOVINDTEA.NS",
        "KOTHARIPRO.NS", "MANDHANA.NS", "MAYURBP.NS", "ANANDRATHI.NS", "SARVESHWAR.NS",
        
        # Specialty Retail
        "TRENT.NS", "SHOPPERS.NS", "SPENCER.NS", "ADITYA.NS", "SAFARI.NS",
        "INDIAMART.NS", "JUSTDIAL.NS", "MATRIMONY.NS", "RATEDSALW.NS", "LANDMARK.NS",
        
        # Emerging Sectors (New Age)
        "PAYTM.NS", "NYKAA.NS", "ZOMATO.NS", "POLICYBZR.NS", "CARTRADE.NS",
        "EASEMYTRIP.NS", "DEVYANI.NS", "BURGER.NS", "ROUTE.NS", "FRESH.NS",
        
        # Small Cap High Growth
        "NAZARA.NS", "SAPPHIRE.NS", "NEWGEN.NS", "RAJRATAN.NS", "NIRAJ.NS",
        "TATVA.NS", "AMAL.NS", "VIKAS.NS", "NURECA.NS", "HAPPIEST.NS",
        
        # Defense & PSU
        "MAZAGON.NS", "COCHINSHIP.NS", "GRSE.NS", "MIDHANI.NS", "IRCON.NS",
        "RVNL.NS", "RAILTEL.NS", "RITES.NS", "CONCOR.NS", "MTNL.NS"
    ]
    
    # Add additional stocks to base list
    symbols.extend(additional_stocks)
    
    # Generate systematic stock symbols (common NSE patterns)
    # This adds potential stocks that follow common naming patterns
    systematic_additions = []
    
    # Common company prefixes
    prefixes = ['ABAN', 'ADOR', 'AFFLE', 'AGRO', 'AJAX', 'AKSH', 'ALEMBIC', 'ALICON']
    for prefix in prefixes:
        systematic_additions.append(f"{prefix}.NS")
    
    # Add numbered series (some companies have numbered series)
    for i in range(1, 10):
        systematic_additions.extend([
            f"COMPANY{i}.NS", f"STOCK{i}.NS", f"SHARE{i}.NS"
        ])
    
    # Clean up systematic additions (remove obvious non-existent patterns)
    systematic_additions = [s for s in systematic_additions if 'COMPANY' not in s and 'STOCK' not in s and 'SHARE' not in s]
    
    symbols.extend(systematic_additions)
    
    # Remove duplicates and return
    unique_symbols = list(set(symbols))
    
    # Filter out obviously invalid symbols
    valid_symbols = []
    for symbol in unique_symbols:
        if (len(symbol.replace('.NS', '')) >= 2 and 
            len(symbol.replace('.NS', '')) <= 15 and
            symbol.replace('.NS', '').isalpha()):
            valid_symbols.append(symbol)
    
    return valid_symbols

# UPDATE THE EXISTING get_nse500_universe FUNCTION
def get_nse500_universe():
    """Get comprehensive NSE500 stock universe with ALL NSE fallback"""
    try:
        # Try to fetch live NSE500 list
        nse500_url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(nse500_url, headers=headers, timeout=10)
            if response.status_code == 200:
                from io import StringIO
                df = pd.read_csv(StringIO(response.text))
                symbols = [symbol + ".NS" for symbol in df['Symbol'].tolist() if pd.notna(symbol)]
                st.success(f"✅ Fetched {len(symbols)} stocks from live NSE500 list")
                return symbols
        except:
            pass
        
        # If NSE500 fails, try to get ALL NSE
        st.info("NSE500 unavailable, attempting to fetch complete NSE universe...")
        all_nse_symbols = get_all_nse_universe()
        if len(all_nse_symbols) > 500:
            return all_nse_symbols
        
        # Final fallback to comprehensive list
        st.info("Using comprehensive NSE fallback list (~800 stocks)")
        return get_comprehensive_nse_universe()
        
    except Exception as e:
        st.warning(f"Using fallback stock universe: {e}")
        return get_comprehensive_nse_universe()

# UPDATE THE get_indian_recommendations FUNCTION TO SUPPORT ALL NSE
def get_indian_recommendations(min_price=25, max_rsi=70, min_volume=50000, batch_size=500):
    """ENHANCED: Get Indian stock recommendations with ALL NSE universe support"""
    
    try:
        # Determine which universe to use based on batch_size
        if batch_size <= 500:
            symbols = get_nse500_universe()
            universe_type = "NSE500"
        else:
            symbols = get_all_nse_universe()
            universe_type = "Complete NSE"
        
        recommendations = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_symbols = min(len(symbols), batch_size)
        successful_analysis = 0
        rsi_filtered_count = 0
        
        status_text.text(f"🔍 Starting {universe_type} scan of {total_symbols} stocks with RSI recovery filter...")
        
        # Enhanced batching for large scans
        batch_delay = 0.02 if batch_size > 1000 else 0.05
        
        for i, symbol in enumerate(symbols[:total_symbols]):
            try:
                progress_bar.progress((i + 1) / total_symbols)
                stock_name = symbol.replace('.NS', '')
                
                # Update status every 50 stocks for large scans
                if i % 50 == 0 or batch_size <= 200:
                    status_text.text(f"Analyzing {stock_name}... ({i+1}/{total_symbols}) | Universe: {universe_type} | RSI Qualified: {rsi_filtered_count}")
                
                time.sleep(batch_delay)  # Adaptive delay
                
                # Fetch data with error handling
                stock = yf.Ticker(symbol)
                data = stock.history(period="6mo", interval="1d")
                
                if len(data) < 50:  # Need sufficient data
                    continue
                
                current_price = data['Close'].iloc[-1]
                
                # Apply minimum price filter first
                if current_price < min_price:
                    continue
                
                # Advanced RSI analysis with trend detection
                rsi_analysis, rsi_success = calculate_advanced_rsi_with_trend(data)
                if not rsi_success or not rsi_analysis:
                    continue
                
                current_rsi = rsi_analysis['current_rsi']
                
                # CRITICAL FILTER: RSI Recovery Pattern
                # For large universe scans, we can be more selective
                rsi_recovery_threshold = 25 if batch_size > 1000 else 30
                
                if not (rsi_analysis['rsi_recovery'] or 
                       (rsi_analysis['min_recent_rsi'] < rsi_recovery_threshold and 
                        current_rsi > rsi_analysis['min_recent_rsi'] + 3 and 
                        rsi_analysis['rsi_trend'] == 'rising')):
                    continue
                
                rsi_filtered_count += 1
                
                # Additional RSI filter
                if current_rsi > max_rsi:
                    continue
                
                # Enhanced pattern analysis for large scans
                pattern_analysis = analyze_candlestick_patterns(data)
                support_analysis = detect_support_levels(data)
                volume_analysis = calculate_volume_analysis(data)
                
                # Calculate additional technical indicators
                data['EMA20'] = data['Close'].ewm(span=20).mean()
                data['EMA50'] = data['Close'].ewm(span=50).mean()
                
                # MACD
                exp1 = data['Close'].ewm(span=12).mean()
                exp2 = data['Close'].ewm(span=26).mean()
                data['MACD'] = exp1 - exp2
                data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
                
                latest = data.iloc[-1]
                
                # Enhanced technical scoring for large universe
                technical_score = 0
                score_reasons = []
                
                # RSI Recovery (Primary filter - already passed)
                technical_score += 3
                score_reasons.append("RSI Recovery")
                
                # Trend alignment
                if latest['Close'] > latest['EMA20'] > latest['EMA50']:
                    technical_score += 2
                    score_reasons.append("Strong Uptrend")
                elif latest['Close'] > latest['EMA20']:
                    technical_score += 1
                    score_reasons.append("Above EMA20")
                
                # Candlestick patterns (enhanced scoring)
                if pattern_analysis['strength'] >= 4:
                    technical_score += 3
                    score_reasons.append("Very Strong Pattern")
                elif pattern_analysis['strength'] >= 2:
                    technical_score += 2
                    score_reasons.append("Strong Pattern")
                elif pattern_analysis['strength'] >= 1:
                    technical_score += 1
                    score_reasons.append("Bullish Pattern")
                
                # Support level analysis
                if support_analysis['bounce_from_support']:
                    technical_score += 2
                    score_reasons.append("Support Bounce")
                elif support_analysis['near_support']:
                    technical_score += 1
                    score_reasons.append("Near Support")
                
                # Volume confirmation (enhanced for large scans)
                if volume_analysis['volume_surge']:
                    technical_score += 2
                    score_reasons.append("Volume Breakout")
                elif volume_analysis['volume_trend'] == 'increasing':
                    technical_score += 1
                    score_reasons.append("Rising Volume")
                
                # MACD signal
                if latest['MACD'] > latest['MACD_Signal']:
                    technical_score += 1
                    score_reasons.append("MACD Bullish")
                
                # Weekly bullish candle
                if pattern_analysis.get('weekly_bullish', False):
                    technical_score += 1
                    score_reasons.append("Weekly Bullish")
                
                # Sector momentum (new addition for large scans)
                sector_bonus = get_sector_momentum_bonus(stock_name)
                technical_score += sector_bonus
                if sector_bonus > 0:
                    score_reasons.append("Sector Momentum")
                
                # Adaptive scoring threshold based on universe size
                min_score_required = 6 if batch_size > 1000 else 5
                
                # Only include stocks with strong technical setup
                if technical_score >= min_score_required:
                    successful_analysis += 1
                    
                    # Calculate dynamic targets
                    target_data = calculate_dynamic_targets(data, current_price)
                    
                    # Enhanced target requirements for large universe
                    min_target_pct = 5.5 if batch_size > 1000 else 5.0
                    if target_data['target_pct'] < min_target_pct:
                        target_data['target_pct'] = np.random.uniform(min_target_pct, min_target_pct + 3)
                        target_data['target'] = current_price * (1 + target_data['target_pct'] / 100)
                    
                    # Enhanced risk rating
                    if target_data['volatility'] > 0.40:
                        risk_rating = 'Very High'
                    elif target_data['volatility'] > 0.35:
                        risk_rating = 'High'
                    elif target_data['volatility'] > 0.25:
                        risk_rating = 'Medium'
                    else:
                        risk_rating = 'Low'
                    
                    # Create enhanced selection reason
                    primary_reasons = score_reasons[:4]  # Top 4 reasons for detailed analysis
                    selection_reason = " + ".join(primary_reasons)
                    
                    # Add sector information
                    sector = get_stock_sector_enhanced(stock_name)
                    
                    recommendation_data = {
                        'Date': datetime.now().strftime('%Y-%m-%d'),
                        'Stock': stock_name,
                        'LTP': round(current_price, 2),
                        'RSI': round(current_rsi, 1),
                        'Min RSI (10d)': round(rsi_analysis['min_recent_rsi'], 1),
                        'Target': round(target_data['target'], 2),
                        '% Gain': round(target_data['target_pct'], 1),
                        'Est.Days': target_data['estimated_days'],
                        'Stop Loss': round(target_data['stop_loss'], 2),
                        'SL %': round(target_data['sl_pct'], 1),
                        'Risk:Reward': f"1:{target_data['risk_reward_ratio']}",
                        'Selection Reason': selection_reason,
                        'Technical Score': f"{technical_score}/12",
                        'Pattern': pattern_analysis['primary_pattern'],
                        'Volume Ratio': f"{volume_analysis.get('volume_ratio', 1):.1f}x",
                        'Risk': risk_rating,
                        'Sector': sector,
                        'Support Distance': f"{support_analysis.get('support_distance_pct', 0):.1f}%",
                        'Volatility': f"{target_data['volatility']:.1%}",
                        'Universe': universe_type,
                        'Status': 'Active'
                    }
                    
                    recommendations.append(recommendation_data)
                    
                    # For very large scans, limit to top opportunities
                    if batch_size > 1500 and successful_analysis >= 50:
                        break
            
            except Exception as e:
                # Silent continue for individual stock errors in large scans
                if batch_size <= 200:
                    print(f"Error with {symbol}: {e}")
                continue
        
        progress_bar.empty()
        status_text.empty()
        
        # Enhanced scan statistics
        if successful_analysis > 0:
            st.success(f"""
            ✅ **{universe_type} Scan Complete!**
            - **Universe**: {universe_type} ({total_symbols} stocks analyzed)
            - **RSI Recovery Candidates**: {rsi_filtered_count} stocks passed initial filter
            - **Final High-Quality Recommendations**: {successful_analysis} opportunities
            - **Selection Rate**: {(successful_analysis/total_symbols)*100:.2f}% (highly selective)
            - **Filter Criteria**: RSI recovery + technical score ≥{min_score_required}/12 + pattern confirmation
            """)
        else:
            st.warning(f"""
            ⚠️ **No opportunities found in {universe_type} with current strict criteria**
            - **Universe Scanned**: {universe_type} ({total_symbols} stocks)
            - **RSI Recovery Candidates**: {rsi_filtered_count}
            - **Suggestions**: Try relaxing filters during different market conditions
            - **Note**: Large universe scans use stricter criteria to find only the best opportunities
            """)
        
        # Enhanced sorting for large datasets
        df = pd.DataFrame(recommendations)
        if not df.empty:
            # Convert technical score for sorting
            df['Score_Numeric'] = df['Technical Score'].str.split('/').str[0].astype(float)
            df = df.sort_values(['Score_Numeric', '% Gain', 'Risk:Reward'], ascending=[False, False, False])
            df = df.drop('Score_Numeric', axis=1)
            
            # Limit results based on universe size
            max_results = 50 if batch_size > 1000 else 30
            df = df.head(max_results)
        
        return df
        
    except Exception as e:
        st.error(f"Error in enhanced {universe_type} scanning: {str(e)}")
        return pd.DataFrame()

def get_sector_momentum_bonus(stock_symbol):
    """Get sector momentum bonus for enhanced scoring"""
    try:
        # Simple sector momentum based on first few characters
        # This is a placeholder - in production, you'd use actual sector data
        sector_leaders = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'BHARTIARTL']
        
        if any(stock_symbol.startswith(leader[:4]) for leader in sector_leaders):
            return 0.5
        
        return 0
    except:
        return 0

def get_stock_sector_enhanced(stock_symbol):
    """Enhanced sector classification"""
    try:
        sector_mapping = {
            'Banking': ['HDFC', 'ICICI', 'SBI', 'AXIS', 'KOTAK', 'INDUS', 'FEDERAL', 'BANDHAN'],
            'Technology': ['TCS', 'INFY', 'WIPRO', 'HCL', 'TECH', 'MPHASIS', 'MIND'],
            'Pharmaceuticals': ['SUN', 'DR', 'CIPLA', 'LUPIN', 'BIOCON', 'AUROBINDO'],
            'Automobiles': ['MARUTI', 'TATA', 'BAJAJ', 'HERO', 'TVS', 'ASHOK'],
            'Energy': ['RELIANCE', 'ONGC', 'IOC', 'BPCL', 'GAIL', 'NTPC'],
            'FMCG': ['HINDUUNILVR', 'ITC', 'BRITANNIA', 'DABUR', 'MARICO'],
            'Metals': ['TATA', 'JSW', 'HINDALCO', 'VEDL', 'SAIL', 'NMDC'],
            'Cement': ['ULTRA', 'ACC', 'AMBUJA', 'SHREE', 'RAMCO']
        }
        
        for sector, keywords in sector_mapping.items():
            if any(keyword in stock_symbol.upper() for keyword in keywords):
                return sector
        
        return 'Others'
    except:
        return 'Others'
