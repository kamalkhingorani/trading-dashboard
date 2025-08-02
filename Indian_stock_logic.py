# indian_stock_logic.py - ENHANCED WITH NSE500 AND ADVANCED RSI SCANNING
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import time
import requests

def get_nse500_universe():
    """Get comprehensive NSE500 stock universe"""
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
        
        # Fallback comprehensive NSE500-like universe
        st.info("Using comprehensive NSE500 fallback list")
        return get_comprehensive_nse_universe()
        
    except Exception as e:
        st.warning(f"Using fallback stock universe: {e}")
        return get_comprehensive_nse_universe()

def get_comprehensive_nse_universe():
    """Comprehensive NSE stock universe covering major sectors"""
    return [
        # NIFTY 50 Large Caps
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
        "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ASIANPAINT.NS", "ITC.NS",
        "AXISBANK.NS", "LT.NS", "SUNPHARMA.NS", "TITAN.NS", "WIPRO.NS",
        "MARUTI.NS", "BAJFINANCE.NS", "TATASTEEL.NS", "ONGC.NS", "COALINDIA.NS",
        "NTPC.NS", "POWERGRID.NS", "ULTRACEMCO.NS", "HCLTECH.NS", "TECHM.NS",
        "NESTLEIND.NS", "HINDUNILVR.NS", "TATAMOTORS.NS", "JSWSTEEL.NS", "BAJAJ-AUTO.NS",
        "HINDALCO.NS", "INDUSINDBK.NS", "ADANIENT.NS", "HEROMOTOCO.NS", "CIPLA.NS",
        "BPCL.NS", "EICHERMOT.NS", "DRREDDY.NS", "APOLLOHOSP.NS", "BRITANNIA.NS",
        "IOC.NS", "DIVISLAB.NS", "GRASIM.NS", "SHREECEM.NS", "BAJAJFINSV.NS",
        "TATACONSUM.NS", "VEDL.NS", "UPL.NS", "LTIM.NS", "ADANIPORTS.NS",
        
        # Banking & Financial Services (Extended)
        "HDFCLIFE.NS", "ICICIGI.NS", "SBILIFE.NS", "BANDHANBNK.NS", "FEDERALBNK.NS",
        "IDFCFIRSTB.NS", "PNB.NS", "CANBK.NS", "BANKBARODA.NS", "UNIONBANK.NS",
        "YESBANK.NS", "IDBI.NS", "RBLBANK.NS", "MANAPPURAM.NS", "MUTHOOTFIN.NS",
        "BAJAJHLDNG.NS", "CHOLAFIN.NS", "LICHSGFIN.NS", "RECLTD.NS", "PFC.NS",
        "IRFC.NS", "HUDCO.NS", "IIFL.NS", "M&MFIN.NS", "SHRIRAMFIN.NS",
        
        # Technology & IT Services (Extended)
        "MPHASIS.NS", "PERSISTENT.NS", "MINDTREE.NS", "COFORGE.NS", "LTTS.NS",
        "OFSS.NS", "RAMCOCEM.NS", "TATAELXSI.NS", "KPITTECH.NS", "CYIENT.NS",
        "ZENSARTECH.NS", "HEXAWARE.NS", "SONATSOFTW.NS", "INTELLECT.NS", "3MINDIA.NS",
        
        # Pharmaceuticals & Healthcare (Extended)
        "AUROPHARMA.NS", "LUPIN.NS", "BIOCON.NS", "CADILAHC.NS", "GLENMARK.NS",
        "TORNTPHARM.NS", "ALKEM.NS", "ABBOTINDIA.NS", "PFIZER.NS", "GSK.NS",
        "FORTIS.NS", "MAXHEALTH.NS", "NHPC.NS", "LAURUSLABS.NS", "SUVEN.NS",
        "STRIDES.NS", "REDDY.NS", "NATCOPHAR.NS", "DIVIS.NS", "GRANULES.NS",
        
        # Consumer Goods & FMCG (Extended)
        "DABUR.NS", "MARICO.NS", "GODREJCP.NS", "COLPAL.NS", "UBL.NS",
        "BATAINDIA.NS", "PAGEIND.NS", "EMAMILTD.NS", "JYOTHYLAB.NS", "RADICO.NS",
        "VBL.NS", "CCL.NS", "RELAXO.NS", "VGUARD.NS", "CROMPTON.NS",
        "BAJAJCONS.NS", "WHIRLPOOL.NS", "VOLTAS.NS", "BLUESTARCO.NS", "AMBER.NS",
        
        # Automobiles & Auto Ancillaries (Extended)
        "M&M.NS", "APOLLOTYRE.NS", "MRF.NS", "MOTHERSON.NS", "BOSCHLTD.NS",
        "BALKRISIND.NS", "ESCORTS.NS", "ASHOKLEY.NS", "BHARATFORG.NS", "ENDURANCE.NS",
        "EXIDEIND.NS", "AMARA.NS", "SUNDARMHLD.NS", "BAJAJHIND.NS", "FORCE.NS",
        "MAHINDCIE.NS", "SPARC.NS", "TIINDIA.NS", "WHEELS.NS", "SUBROS.NS",
        
        # Oil, Gas & Energy (Extended)
        "HINDPETRO.NS", "GAIL.NS", "ADANIPOWER.NS", "TATAPOWER.NS", "JSW.NS",
        "ADANIGREEN.NS", "TORNTPOWER.NS", "RPOWER.NS", "ADANITRANS.NS", "JPPOWER.NS",
        "NHPC.NS", "SJVN.NS", "THERMAX.NS", "BHEL.NS", "SUZLON.NS",
        "INOXWIND.NS", "ORIENTREF.NS", "MRPL.NS", "CESC.NS", "ADANIGAS.NS",
        
        # Metals & Mining (Extended)
        "SAIL.NS", "NMDC.NS", "JINDALSTEL.NS", "HINDZINC.NS", "WELCORP.NS",
        "RATNAMANI.NS", "MOIL.NS", "GRAPHITE.NS", "NATIONALUM.NS", "BALRAMCHIN.NS",
        "JSHL.NS", "KALYANKJIL.NS", "WELSPUNIND.NS", "GALLANTT.NS", "JINDALSAW.NS",
        
        # Cement & Construction (Extended)
        "ACC.NS", "AMBUJACEMENT.NS", "HEIDELBERG.NS", "RAMCOCEM.NS", "JKCEMENT.NS",
        "KAKATCEM.NS", "DECCANCEMENT.NS", "BIRLACEM.NS", "PRISMCEM.NS", "ORIENTCEM.NS",
        "DLF.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PRESTIGE.NS", "BRIGADE.NS",
        
        # Textiles & Apparel (Extended)
        "RTNINFRA.NS", "VARDHMAN.NS", "WELSPUNIND.NS", "ARVIND.NS", "RAYMOND.NS",
        "GRASIM.NS", "PAGEIND.NS", "ADITYANB.NS", "TEXRAIL.NS", "RSWM.NS",
        
        # Chemicals & Petrochemicals (Extended)
        "PIDILITIND.NS", "BERGEPAINT.NS", "ASIANPAINT.NS", "KANSAINER.NS", "AKZONOBEL.NS",
        "AAVAS.NS", "DEEPAKNTR.NS", "GNFC.NS", "GSFC.NS", "RCF.NS",
        "CHAMBLFERT.NS", "COROMANDEL.NS", "FACT.NS", "NFL.NS", "ZUARI.NS",
        
        # Industrial & Infrastructure (Extended)
        "HAVELLS.NS", "POLYCAB.NS", "KEI.NS", "FINOLEX.NS", "VGUARD.NS",
        "SIEMENS.NS", "ABB.NS", "SCHNEIDER.NS", "HONAUT.NS", "THERMAX.NS",
        "CUMMINSIND.NS", "MAHSEAMLES.NS", "TIMKEN.NS", "SKFINDIA.NS", "NBCC.NS",
        "IRCON.NS", "RVNL.NS", "CONCOR.NS", "CONTAINER.NS", "ADANIPORTS.NS",
        
        # Telecom & Media (Extended)
        "HFCL.NS", "GTPL.NS", "TEJAS.NS", "RAILTEL.NS", "ROUTE.NS",
        "ZEEL.NS", "SUNTV.NS", "NETWORKE18.NS", "TVTODAY.NS", "JAGRAN.NS",
        
        # Retail & E-commerce (Extended)
        "TRENT.NS", "SHOPPERS.NS", "SPENCER.NS", "ADITYA.NS", "V2RETAIL.NS",
        "INDIAMART.NS", "JUSTDIAL.NS", "NAUKRI.NS", "MINDTECK.NS", "MATRIMONY.NS",
        
        # Airlines & Logistics (Extended)
        "INDIGO.NS", "SPICEJET.NS", "BLUEDART.NS", "GATI.NS", "MAHLOG.NS",
        "AEGISCHEM.NS", "TITAGARH.NS", "TIINDIA.NS", "RSWM.NS", "TEXRAIL.NS",
        
        # Defense & Government (Extended)
        "BEL.NS", "HAL.NS", "BEML.
