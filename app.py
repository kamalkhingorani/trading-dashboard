@st.cache_data(ttl=86400)
def get_complete_sp500_universe():
    """Complete S&P 500 with comprehensive sector coverage"""
    sp500_universe = [
        # TECHNOLOGY & SOFTWARE
        "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "TSLA", "META", "NVDA", "NFLX", "ADBE",
        "CRM", "ORCL", "INTC", "AMD", "QCOM", "AVGO", "CSCO", "IBM", "INTU", "NOW",
        "WDAY", "VEEV", "DDOG", "SNOW", "CRWD", "ZS", "OKTA", "SPLK", "MDB", "NET",
        "TEAM", "ATLASSIAN", "SHOP", "SQ", "PYPL", "ADSK", "ANSS", "CDNS", "SNPS", "FTNT",
        "PANW", "CYBR", "TENB", "QLYS", "ESTC", "DOMO", "TWLO", "ZM", "DOCU", "UBER",
        
        # FINANCIAL SERVICES & BANKING
        "JPM", "BAC", "WFC", "GS", "MS", "C", "AXP", "V", "MA", "PYPL",
        "BK", "USB", "PNC", "COF", "SCHW", "BLK", "SPGI", "MCO", "AIG", "TRV",
        "ALL", "PGR", "CB", "AON", "MMC", "MSCI", "ICE", "CME", "NDAQ", "CBOE",
        "KKR", "BX", "APO", "CG", "OWL", "ARES", "TPG", "HLNE", "BLUE", "EQH",
        
        # HEALTHCARE & PHARMACEUTICALS
        "JNJ", "PFE", "UNH", "ABBV", "TMO", "ABT", "MDT", "BMY", "AMGN", "GILD",
        "REGN", "BSX", "SYK", "ISRG", "ZBH", "BDX", "EW", "ALGN", "MRNA", "BNTX",
        "DHR", "A", "BAX", "BIO", "TECH", "PKI", "WAT", "MTD", "TFX", "WST",
        "CVS", "CI", "ANTM", "HUM", "CNC", "MOH", "ELV", "HCA", "THC", "UHS",
        "BIIB", "VRTX", "ILMN", "DXCM", "PODD", "TNDM", "OMCL", "TDOC", "HOLX", "VAR",
        
        # DEFENSE & AEROSPACE
        "BA", "LMT", "RTX", "NOC", "GD", "LHX", "LDOS", "HII", "TDG", "CW",
        "SPR", "AIR", "KTOS", "AVX", "HEI", "TXT", "PH", "ROL", "CACI", "SAIC",
        
        # MANUFACTURING & INDUSTRIALS
        "CAT", "GE", "MMM", "HON", "UPS", "FDX", "EMR", "ETN", "ITW", "PH",
        "CMI", "DE", "DOV", "ROK", "PNR", "AME", "ROP", "FTV", "XYL", "ITT",
        "IR", "GNRC", "CARR", "OTIS", "PCAR", "CMI", "WAB", "CHRW", "JBHT", "EXPD",
        "NSC", "CSX", "UNP", "KSU", "CNI", "CP", "TRN", "GWR", "RAIL", "GATX",
        
        # ENERGY & UTILITIES
        "XOM", "CVX", "COP", "EOG", "SLB", "MPC", "VLO", "PSX", "OXY", "HAL",
        "DVN", "FANG", "APA", "EQT", "COG", "MRO", "CNX", "RRC", "AR", "SM",
        "KMI", "WMB", "OKE", "EPD", "ET", "MPLX", "PAA", "WES", "ENLC", "SMLP",
        import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import feedparser
from datetime import datetime, timedelta
import numpy as np
import time
import gc
import random

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
    .batch-tracker {
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
    .coverage-info {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Complete stock universes for rotating batches
@st.cache_data(ttl=86400)
def get_complete_nse_universe():
    """Complete NSE universe with ALL critical sectors for professional trading"""
    nse_universe = [
        # LARGE CAP - Nifty 50 Core
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
        "ICICIBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ASIANPAINT.NS",
        "ITC.NS", "AXISBANK.NS", "LT.NS", "SUNPHARMA.NS", "TITAN.NS",
        "WIPRO.NS", "NESTLEIND.NS", "ULTRACEMCO.NS", "POWERGRID.NS", "NTPC.NS",
        "TECHM.NS", "HCLTECH.NS", "MARUTI.NS", "BAJFINANCE.NS", "TATASTEEL.NS",
        "ONGC.NS", "COALINDIA.NS", "DRREDDY.NS", "BAJAJFINSV.NS", "INDUSINDBK.NS",
        "BRITANNIA.NS", "DIVISLAB.NS", "GRASIM.NS", "HEROMOTOCO.NS", "JSWSTEEL.NS",
        "CIPLA.NS", "EICHERMOT.NS", "BPCL.NS", "HINDALCO.NS", "SHREECEM.NS",
        "ADANIPORTS.NS", "APOLLOHOSP.NS", "TATACONSUM.NS", "IOC.NS", "TATAMOTORS.NS",
        "GODREJCP.NS", "SBILIFE.NS", "HDFCLIFE.NS", "BAJAJ-AUTO.NS", "M&M.NS",
        
        # BANKING & FINANCIAL SERVICES (Complete Coverage)
        "BANKBARODA.NS", "BANKINDIA.NS", "CANBK.NS", "CENTRALBK.NS", "IDBIGOLD.NS",
        "INDIANB.NS", "IOB.NS", "MAHABANK.NS", "ORIENTBANK.NS", "PNB.NS",
        "PUNJABSIND.NS", "SOUTHBANK.NS", "SYNDIBANK.NS", "UNIONBANK.NS", "UCOBANK.NS",
        "RBLBANK.NS", "YESBANK.NS", "EQUITAS.NS", "DCBBANK.NS", "CITYUNION.NS",
        "KARURVYSYA.NS", "NAINITAL.NS", "COSMOS.NS", "DHANLAXMI.NS", "JKBANK.NS",
        "FEDERALBNK.NS", "IDFCFIRSTB.NS", "BANDHANBNK.NS", "AUBANK.NS", "UJJIVAN.NS",
        "CHOLAFIN.NS", "BAJAJHLDNG.NS", "IIFL.NS", "MUTHOOTFIN.NS", "MANAPPURAM.NS",
        "SRTRANSFIN.NS", "L&TFH.NS", "PFC.NS", "RECLTD.NS", "IRFC.NS",
        "HUDCO.NS", "LICHSGFIN.NS", "CANFINHOME.NS", "AAVAS.NS", "IBULHSGFIN.NS",
        
        # DEFENSE & AEROSPACE (Critical for National Security)
        "HAL.NS", "BEL.NS", "BEML.NS", "BDL.NS", "GARDENREACH.NS", "GRSE.NS",
        "MAZAGON.NS", "MDL.NS", "MIDHANI.NS", "ORDNANCEFTY.NS", "BHEL.NS",
        "COCHINSHIP.NS", "TIINDIA.NS", "DYNAMATECH.NS", "ASTRAZEN.NS", "IDEAFORGE.NS",
        "NEWGEN.NS", "CENTUM.NS", "DATAPATTNS.NS", "PARAS.NS", "MUNJALAU.NS",
        
        # INFRASTRUCTURE & CONSTRUCTION (Key Growth Driver)
        "LT.NS", "UBL.NS", "HCC.NS", "IRB.NS", "SADBHAV.NS", "DILIPBUILDCON.NS",
        "PNCINFRA.NS", "JPASSOCIAT.NS", "NCC.NS", "ASHOKA.NS", "JKCEMENT.NS",
        "HEIDELBERG.NS", "RAMCOCEM.NS", "DALBHARAT.NS", "INDIACEM.NS", "STARCEMENT.NS",
        "PRISMCEM.NS", "ORIENTCEM.NS", "DECCAN.NS", "MAGMA.NS", "JAICORPLTD.NS",
        "PRAKASH.NS", "HTMEDIA.NS", "GMR.NS", "GMRINFRA.NS", "GVK.NS",
        "KALPATPOWR.NS", "THERMAX.NS", "BGRENERGY.NS", "RPOWER.NS", "ADANIPOWER.NS",
        "TORNTPOWER.NS", "ADANIGREEN.NS", "RENUKA.NS", "SUZLON.NS", "INOXWIND.NS",
        
        # RETAIL & CONSUMER (Massive Sector)
        "DMART.NS", "SHOPPERS.NS", "TRENT.NS", "JUBLFOOD.NS", "WESTLIFE.NS",
        "DEVYANI.NS", "SPECIALITY.NS", "RELAXO.NS", "BATA.NS", "BATAINDIA.NS",
        "RUPA.NS", "GOKEX.NS", "SIYARAM.NS", "RAYMOND.NS", "ARVIND.NS",
        "CENTURYTEX.NS", "WELCORP.NS", "TEXRAIL.NS", "VARDHMAN.NS", "ALOKTEXT.NS",
        "MARICO.NS", "DABUR.NS", "GODREJCP.NS", "EMAMILTD.NS", "VIPIND.NS",
        "COLPAL.NS", "GILLETTE.NS", "HONASA.NS", "NYKAA.NS", "FINCABLES.NS",
        
        # MANUFACTURING & INDUSTRIALS (Make in India Focus)
        "BHEL.NS", "BEL.NS", "BEML.NS", "TIINDIA.NS", "CUMMINSIND.NS", "ABB.NS",
        "SIEMENS.NS", "SCHNEIDER.NS", "ORIENTELEC.NS", "HAVELLS.NS", "POLYCAB.NS",
        "FINOLEX.NS", "KEI.NS", "VINDHYATEL.NS", "RKFORGE.NS", "RATNAMANI.NS",
        "WELCORP.NS", "TEXINFRA.NS", "SONACOMS.NS", "MOTHERSUMI.NS", "BOSCHLTD.NS",
        "ESCORTS.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "TVSMOTOR.NS", "EICHERMOT.NS",
        "ASHOKLEY.NS", "MAHINDCIE.NS", "BHARATFORG.NS", "SUBROS.NS", "GABRIEL.NS",
        "ENDURANCE.NS", "SUPRAJIT.NS", "SUNDRMFAST.NS", "MINDAIND.NS", "CRAFTSMAN.NS",
        
        # HEALTHCARE & PHARMACEUTICALS (Complete Ecosystem)
        "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "LUPIN.NS",
        "BIOCON.NS", "TORNTPHARM.NS", "CADILAHC.NS", "GLENMARK.NS", "WOCKPHARMA.NS",
        "STRIDES.NS", "AJANTPHARM.NS", "ALKEM.NS", "MANKIND.NS", "GRANULES.NS",
        "IPCALAB.NS", "NEULANDLAB.NS", "NATCOPHAR.NS", "SOLARA.NS", "DRREDDYS.NS",
        "PFIZER.NS", "SANOFI.NS", "ABBOTINDIA.NS", "GSKCONS.NS", "JBCHEPHARM.NS",
        "ZYDUSWELL.NS", "STAR.NS", "REDDY.NS", "AUROPHARMA.NS", "SEQUENT.NS",
        "APOLLOHOSP.NS", "FORTIS.NS", "MAXHEALTH.NS", "NARAYANHRY.NS", "CARERATING.NS",
        "STARHEALTH.NS", "LALPATHLAB.NS", "METROPOLIS.NS", "THYROCARE.NS", "KRSNAA.NS",
        "RAINBOW.NS", "MEDPLUS.NS", "PHLX.NS", "VENKEYS.NS", "SUVEN.NS",
        
        # TECHNOLOGY & SOFTWARE (Digital India)
        "TCS.NS", "INFY.NS", "WIPRO.NS", "TECHM.NS", "HCLTECH.NS", "LTI.NS",
        "MINDTREE.NS", "MPHASIS.NS", "COFORGE.NS", "PERSISTENT.NS", "LTTS.NS",
        "CYIENT.NS", "ECLERX.NS", "FIRSTSOURCE.NS", "HEXAWARE.NS", "KPIT.NS",
        "NIITLTD.NS", "ROLTA.NS", "ZENSAR.NS", "POLARIS.NS", "INTELLECT.NS",
        "NEWGEN.NS", "RAMKY.NS", "SAKSOFT.NS", "MASTEK.NS", "INFRATEL.NS",
        "TATAELXSI.NS", "NELCO.NS", "INDIAINFO.NS", "SOFTTECH.NS", "RSYSTEMS.NS",
        
        # AUTOMOTIVE & AUTO COMPONENTS (Mobility Revolution)
        "MARUTI.NS", "TATAMOTORS.NS", "M&M.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS",
        "TVSMOTOR.NS", "EICHERMOT.NS", "ASHOKLEY.NS", "MAHINDCIE.NS", "BHARATFORG.NS",
        "MOTHERSUMI.NS", "BOSCHLTD.NS", "ESCORTS.NS", "BALKRISIND.NS", "MRF.NS",
        "APOLLOTYRE.NS", "CEAT.NS", "JK TYRE.NS", "GOODYEAR.NS", "SUBROS.NS",
        "GABRIEL.NS", "ENDURANCE.NS", "SUPRAJIT.NS", "SUNDRMFAST.NS", "MINDAIND.NS",
        "CRAFTSMAN.NS", "TEAMLEASE.NS", "FIEM.NS", "SETCO.NS", "RANE.NS",
        
        # ENERGY & POWER (Critical Infrastructure)
        "RELIANCE.NS", "ONGC.NS", "IOC.NS", "BPCL.NS", "HPCL.NS", "GAIL.NS",
        "OIL.NS", "MRPL.NS", "CHENNPETRO.NS", "GSPL.NS", "IGL.NS", "MGL.NS",
        "PETRONET.NS", "NTPC.NS", "POWERGRID.NS", "NHPC.NS", "SJVN.NS", "THDC.NS",
        "RPOWER.NS", "ADANIPOWER.NS", "TORNTPOWER.NS", "JSWENERGY.NS", "TATAPWR.NS",
        "CESC.NS", "TORNTPHARM.NS", "ADANIGREEN.NS", "RENUKA.NS", "SUZLON.NS",
        "INOXWIND.NS", "WEBSOL.NS", "SOLARA.NS", "BOROSIL.NS", "HFCL.NS",
        
        # METALS & MINING (Commodity Play)
        "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "SAIL.NS",
        "JINDALSTEL.NS", "NMDC.NS", "MOIL.NS", "COALINDIA.NS", "HEG.NS",
        "GRAPHITE.NS", "WELCORP.NS", "RATNAMANI.NS", "APL.NS", "KALYANI.NS",
        "MAHINDCIE.NS", "BHARATFORG.NS", "RAMCOCEM.NS", "DALBHARAT.NS", "HEIDELBERG.NS",
        "JKCEMENT.NS", "INDIACEM.NS", "STARCEMENT.NS", "PRISMCEM.NS", "ORIENTCEM.NS",
        
        # AGRICULTURE & FERTILIZERS (Food Security)
        "UBL.NS", "CHAMBLFERT.NS", "COROMANDEL.NS", "GSFC.NS", "NFL.NS",
        "RCF.NS", "FACT.NS", "DEEPAKNTR.NS", "GNFC.NS", "KRIBHCO.NS",
        "MANGALAM.NS", "MADRASFERT.NS", "ZUARI.NS", "PARADEEP.NS", "SRF.NS",
        "ATUL.NS", "TATACHEMICALS.NS", "NOCIL.NS", "ALKYLAMINE.NS", "BALAJI.NS",
        "BASF.NS", "NAVIN.NS", "FLUOROCHEM.NS", "GHCL.NS", "PIDILITE.NS",
        
        # TELECOM & MEDIA (Digital Connectivity)
        "BHARTIARTL.NS", "IDEA.NS", "RCOM.NS", "GTLINFRA.NS", "GTPL.NS",
        "HATHWAY.NS", "SITI.NS", "DISHTV.NS", "TATACOMM.NS", "RAILTEL.NS",
        "ZEEL.NS", "SUNTV.NS", "PVRINOX.NS", "INOXLEISUR.NS", "GIPCL.NS",
        "NETWORK18.NS", "TVTODAY.NS", "JAGRAN.NS", "HTMEDIA.NS", "SAREGAMA.NS",
        
        # TRANSPORT & LOGISTICS (Supply Chain)
        "CONCOR.NS", "IRCTC.NS", "GATI.NS", "BLUEDART.NS", "TCIEXPRESS.NS",
        "MAHLOG.NS", "DELHIVERY.NS", "DTDC.NS", "VAGAS.NS", "SNOWMAN.NS",
        "COLDEX.NS", "ALLCARGO.NS", "EXIDEIND.NS", "AMARARAJA.NS", "HBL.NS",
        
        # REAL ESTATE & HOUSING (Urbanization Play)
        "DLF.NS", "GODREJPROP.NS", "SOBHA.NS", "BRIGADE.NS", "PRESTIGE.NS",
        "KOLTEPATIL.NS", "PURAVANKARA.NS", "MAHLIFE.NS", "SUNTECK.NS", "PHOENIXLTD.NS",
        "OBEROIRLTY.NS", "UNITECH.NS", "ASHIANA.NS", "HOMESFIRST.NS", "VAIBHAVGBL.NS",
        "MACROTECH.NS", "LODHA.NS", "SIGNATURE.NS", "BROOKFIELD.NS", "EMBASSY.NS",
        
        # FMCG & CONSUMER GOODS (Daily Consumption)
        "HINDUNILVR.NS", "ITC.NS", "BRITANNIA.NS", "NESTLEIND.NS", "DABUR.NS",
        "MARICO.NS", "GODREJCP.NS", "COLPAL.NS", "EMAMILTD.NS", "VIPIND.NS",
        "BAJAJCONS.NS", "JYOTHYLAB.NS", "VBLVOL.NS", "RADICO.NS", "UBL.NS",
        "MCDOWELL-N.NS", "GLOBALBEES.NS", "HONASA.NS", "GILLETTE.NS", "PRATAPOIL.NS",
        
        # TEXTILES & FASHION (Export Oriented)
        "RAYMOND.NS", "ARVIND.NS", "WELCORP.NS", "CENTURYTEX.NS", "ALOKTEXT.NS",
        "VARDHMAN.NS", "TRIDENT.NS", "HIMATSEIDE.NS", "KPRMILL.NS", "SPENTEX.NS",
        "TEXRAIL.NS", "RIIL.NS", "RSWM.NS", "INDORAMA.NS", "FILATEX.NS",
        
        # NEW AGE & TECH STARTUPS (Digital Economy)
        "ZOMATO.NS", "NYKAA.NS", "PAYTM.NS", "POLICYBZR.NS", "DELHIVERY.NS",
        "EASEMYTRIP.NS", "CARTRADE.NS", "MATRIMONY.NS", "JUSTDIAL.NS", "INDIAMART.NS",
        "NAZARA.NS", "CAMPUS.NS", "DEVYANI.NS", "SAPPHIRE.NS", "TATVA.NS",
        "METRO.NS", "CLEAN.NS", "LAXMI.NS", "SIGNATURE.NS", "STARHEALTH.NS"
    ]
    return nse_universe[:400]  # Comprehensive coverage - 400 stocks across ALL sectors

@st.cache_data(ttl=86400)
def get_complete_sp500_universe():
    """Complete S&P 500 universe for rotating batches"""
    sp500_universe = [
        # Tech Giants
        "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "TSLA", "META", "NVDA", "NFLX", "ADBE",
        "CRM", "ORCL", "INTC", "AMD", "QCOM", "AVGO", "CSCO", "IBM", "INTU", "NOW",
        "WDAY", "VEEV", "DDOG", "SNOW", "CRWD", "ZS", "OKTA", "SPLK", "MDB", "NET",
        
        # Financial Services
        "JPM", "BAC", "WFC", "GS", "MS", "C", "AXP", "V", "MA", "PYPL",
        "BK", "USB", "PNC", "COF", "SCHW", "BLK", "SPGI", "MCO", "AIG", "TRV",
        "ALL", "PGR", "CB", "AON", "MMC", "MSCI", "ICE", "CME", "NDAQ", "CBOE",
        
        # Healthcare & Pharmaceuticals
        "JNJ", "PFE", "UNH", "ABBV", "TMO", "ABT", "MDT", "BMY", "AMGN", "GILD",
        "REGN", "BSX", "SYK", "ISRG", "ZBH", "BDX", "EW", "ALGN", "MRNA", "BNTX",
        "DHR", "A", "BAX", "BIO", "TECH", "PKI", "WAT", "MTD", "TFX", "WST",
        
        # Consumer Discretionary & Staples
        "WMT", "HD", "LOW", "COST", "TGT", "PG", "KO", "PEP", "MCD", "SBUX",
        "NKE", "TJX", "ROST", "YUM", "CMG", "ULTA", "ETSY", "EBAY", "DIS", "F",
        "GM", "TSLA", "LCID", "RIVN", "KMX", "AN", "LAD", "ABG", "SAH", "LEN",
        
        # Industrial & Materials
        "BA", "CAT", "GE", "MMM", "HON", "UPS", "FDX", "XOM", "CVX", "COP",
        "EOG", "SLB", "MPC", "VLO", "PSX", "OXY", "HAL", "DVN", "FANG", "APA",
        "LIN", "APD", "ECL", "SHW", "FCX", "NEM", "FMC", "ALB", "EMN", "IFF",
        
        # Communication Services
        "VZ", "T", "TMUS", "CMCSA", "CHTR", "FOXA", "FOX", "NWSA", "NWS", "PARA",
        "WBD", "DISH", "SIRI", "TWTR", "SNAP", "PINS", "MTCH", "ZM", "DOCU", "UBER",
        
        # Utilities & REITs
        "NEE", "DUK", "SO", "AEP", "EXC", "XEL", "WEC", "ES", "AWK", "CMS",
        "CNP", "NI", "LNT", "EVRG", "ATO", "NRG", "PEG", "EIX", "PCG", "ED",
        "AMT", "PLD", "EQIX", "SPG", "O", "PSA", "EQR", "AVB", "ARE", "DLR",
        
        # Energy & Materials Extended
        "KMI", "WMB", "OKE", "EPD", "ET", "MPLX", "PAA", "WES", "ENLC", "SMLP",
        "PPG", "CF", "MOS", "LYB", "DOW", "DD", "CE", "VMC", "MLM", "NUE",
        
        # Healthcare Extended
        "CVS", "CI", "ANTM", "HUM", "CNC", "MOH", "ELV", "HCA", "THC", "UHS",
        "DXCM", "PODD", "TNDM", "OMCL", "TDOC", "VEEV", "ZBH", "HOLX", "VAR", "NVST",
        
        # Technology Extended
        "TEAM", "ATLASSIAN", "SHOP", "SQ", "PYPL", "ADSK", "ANSS", "CDNS", "SNPS", "FTNT",
        "PANW", "CYBR", "TENB", "RPD", "QLYS", "FEYE", "VRNS", "SAIL", "ESTC", "DOMO",
        
        # Consumer Extended
        "AMZN", "BABA", "JD", "PDD", "MELI", "SE", "GRAB", "UBER", "LYFT", "DASH",
        "ABNB", "BKNG", "EXPE", "TRIP", "NCLH", "CCL", "RCL", "MAR", "HLT", "H",
        
        # Biotech & Pharma Extended
        "BIIB", "CELG", "VRTX", "ILMN", "ALXN", "INCY", "EXAS", "ARWR", "BEAM", "CRSP",
        "EDIT", "NTLA", "BLUE", "FOLD", "MRNA", "BNTX", "NVAX", "INO", "OCGN", "VXRT"
    ]
    return sp500_universe[:250]  # Limit to 250 for manageable scanning

def calculate_rsi(data, window=14):
    """Memory-efficient RSI calculation"""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_next_batch(symbols, batch_size, current_batch_num):
    """Get the next batch of symbols for scanning"""
    total_batches = (len(symbols) + batch_size - 1) // batch_size
    
    # Rotate to next batch
    start_idx = (current_batch_num * batch_size) % len(symbols)
    end_idx = min(start_idx + batch_size, len(symbols))
    
    # Handle wrap-around
    if end_idx - start_idx < batch_size and start_idx > 0:
        # Get remaining symbols from beginning
        remaining_needed = batch_size - (end_idx - start_idx)
        batch = symbols[start_idx:end_idx] + symbols[:remaining_needed]
        next_batch_num = (current_batch_num + 1) % total_batches
    else:
        batch = symbols[start_idx:end_idx]
        next_batch_num = (current_batch_num + 1) % total_batches
    
    return batch, next_batch_num, total_batches

def scan_rotating_batch(symbols, min_price, max_rsi, market_type, batch_size, current_batch_num):
    """Scan the current batch and prepare for next rotation"""
    
    # Get current batch
    current_batch, next_batch_num, total_batches = get_next_batch(symbols, batch_size, current_batch_num)
    
    st.markdown(f"""
    <div class="batch-tracker">
    <strong>📊 Batch Coverage Tracker</strong><br>
    🔄 <strong>Current Batch:</strong> {current_batch_num + 1} of {total_batches}<br>
    📈 <strong>Scanning:</strong> {len(current_batch)} stocks from {market_type} universe<br>
    🎯 <strong>Next Refresh:</strong> Will scan batch {next_batch_num + 1}<br>
    📋 <strong>Total Coverage:</strong> {len(symbols)} stocks across all batches
    </div>
    """, unsafe_allow_html=True)
    
    recommendations = []
    
    progress_bar = st.progress(0)
    status_placeholder = st.empty()
    
    for i, symbol in enumerate(current_batch):
        try:
            progress = (i + 1) / len(current_batch)
            progress_bar.progress(progress)
            status_placeholder.text(f"Scanning {symbol} ({i+1}/{len(current_batch)}) - Batch {current_batch_num + 1}/{total_batches}")
            
            # Fetch stock data
            stock = yf.Ticker(symbol)
            data = stock.history(period="3mo", interval="1d")
            
            if data.empty or len(data) < 50:
                continue
            
            # Calculate indicators
            data['RSI'] = calculate_rsi(data)
            data['EMA20'] = data['Close'].ewm(span=20).mean()
            data['EMA50'] = data['Close'].ewm(span=50).mean()
            data['Volume_MA'] = data['Volume'].rolling(window=20).mean()
            
            latest = data.iloc[-1]
            current_price = latest['Close']
            rsi = latest['RSI']
            
            if pd.isna(rsi) or pd.isna(current_price):
                continue
            
            volume_ratio = latest['Volume'] / max(latest.get('Volume_MA', latest['Volume']), 1)
            
            # Enhanced filtering for better opportunities
            price_filter = current_price >= min_price
            rsi_filter = rsi <= max_rsi
            volume_filter = volume_ratio > 1.0  # Above average volume
            trend_filter = latest['Close'] > latest['EMA20']
            momentum_filter = latest['EMA20'] > latest['EMA50']
            
            if price_filter and rsi_filter and volume_filter and trend_filter:
                # Calculate volatility-based targets
                returns = data['Close'].pct_change().dropna()
                volatility = returns.std()
                
                if market_type == "Indian":
                    if volatility > 0.03:
                        target_pct = 0.12  # 12% for high volatility
                        days_estimate = 12
                    elif volatility > 0.02:
                        target_pct = 0.08  # 8% for medium volatility
                        days_estimate = 15
                    else:
                        target_pct = 0.06  # 6% for low volatility
                        days_estimate = 20
                    sl_pct = 0.07
                else:  # US market
                    if volatility > 0.025:
                        target_pct = 0.10  # 10% for high volatility
                        days_estimate = 10
                    elif volatility > 0.018:
                        target_pct = 0.07  # 7% for medium volatility
                        days_estimate = 12
                    else:
                        target_pct = 0.05  # 5% for low volatility
                        days_estimate = 18
                    sl_pct = 0.06
                
                target = current_price * (1 + target_pct)
                sl = current_price * (1 - sl_pct)
                
                # Quality score based on multiple factors
                quality_score = 0
                if volume_ratio > 1.5: quality_score += 1  # High volume
                if momentum_filter: quality_score += 1      # EMA alignment
                if rsi < 30: quality_score += 1             # Oversold
                if volatility > 0.02: quality_score += 1    # Good movement potential
                
                recommendations.append({
                    'Date': datetime.now().strftime('%Y-%m-%d'),
                    'Stock': symbol.replace('.NS', '') if market_type == "Indian" else symbol,
                    'LTP': round(current_price, 2),
                    'RSI': round(rsi, 1),
                    'Target': round(target, 2),
                    '% Gain': round(target_pct * 100, 1),
                    'Est. Days': days_estimate,
                    'Stop Loss': round(sl, 2),
                    'Volume Ratio': round(volume_ratio, 2),
                    'Quality Score': quality_score,
                    'Batch': f"{current_batch_num + 1}/{total_batches}",
                    'Status': 'Active'
                })
            
            # Clear data to save memory
            del data
            
        except Exception:
            continue
    
    progress_bar.empty()
    status_placeholder.empty()
    
    # Update session state with next batch number
    return pd.DataFrame(recommendations), next_batch_num

def fetch_news_optimized():
    """Fetch news efficiently"""
    sources = {
        'Economic Times': 'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
        'Moneycontrol': 'https://www.moneycontrol.com/rss/business.xml',
        'Business Standard': 'https://www.business-standard.com/rss/markets-106.rss'
    }
    
    all_news = []
    for source_name, url in sources.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:12]:  # More news items
                title = entry.get('title', 'No Title')
                summary = entry.get('summary', entry.get('description', ''))[:400]
                link = entry.get('link', '#')
                
                text = (title + " " + summary).lower()
                
                if any(word in text for word in ['rbi', 'policy', 'rate', 'budget']):
                    category, impact = 'RBI/Policy', 'High'
                elif any(word in text for word in ['earnings', 'results', 'profit']):
                    category, impact = 'Corporate Earnings', 'Medium'
                elif any(word in text for word in ['fii', 'dii', 'investment', 'inflow']):
                    category, impact = 'FII/DII Activity', 'High'
                elif any(word in text for word in ['crude', 'oil', 'commodity']):
                    category, impact = 'Commodities', 'Medium'
                elif any(word in text for word in ['rupee', 'dollar', 'currency']):
                    category, impact = 'Currency', 'Medium'
                else:
                    category, impact = 'Market News', 'Low'
                
                all_news.append({
                    'title': title, 'summary': summary, 'category': category,
                    'market_impact': impact, 'source': source_name, 'link': link,
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'time': datetime.now().strftime('%H:%M')
                })
        except:
            continue
    
    impact_order = {'High': 3, 'Medium': 2, 'Low': 1}
    all_news.sort(key=lambda x: impact_order.get(x['market_impact'], 0), reverse=True)
    return all_news[:40]  # More news items

# Initialize session state for batch tracking
if 'indian_recos' not in st.session_state:
    st.session_state.indian_recos = pd.DataFrame()
if 'us_recos' not in st.session_state:
    st.session_state.us_recos = pd.DataFrame()
if 'news_data' not in st.session_state:
    st.session_state.news_data = []
if 'nse_batch_num' not in st.session_state:
    st.session_state.nse_batch_num = 0
if 'sp500_batch_num' not in st.session_state:
    st.session_state.sp500_batch_num = 0
if 'scan_history' not in st.session_state:
    st.session_state.scan_history = []

# Main title
st.markdown('<h1 class="main-header">📈 Kamal\'s Trading Dashboard</h1>', unsafe_allow_html=True)

# Professional usage info
st.markdown("""
<div class="opportunity-alert">
<strong>💼 Professional Trading Assistant</strong><br>
🔄 <strong>Rotating Batch System</strong>: Each refresh scans the next batch - complete market coverage!<br>
📊 <strong>For Broking Associates</strong>: Comprehensive stock universe scanning for client recommendations<br>
⏰ <strong>Time-Efficient</strong>: Automated technical analysis across entire NSE/S&P 500 universe<br>
💰 <strong>Revenue Optimization</strong>: Never miss opportunities across the complete market
</div>
""", unsafe_allow_html=True)

# Load stock universes
nse_universe = get_complete_nse_universe()
sp500_universe = get_complete_sp500_universe()

# Sidebar
st.sidebar.title("Professional Controls")
st.sidebar.markdown(f"""
**🎯 Complete Sector Coverage**
🇮🇳 NSE: {len(nse_universe)} stocks
• Defense & Aerospace
• Infrastructure & Construction  
• Manufacturing & Auto
• Healthcare & Pharma
• Banking & Financial
• Energy & Power
• Technology & Software
• Retail & Consumer
• Metals & Mining
• Agriculture & Fertilizers
• Telecom & Media
• Real Estate & Housing
• FMCG & Textiles
• New Age & Startups

🇺🇸 S&P 500: {len(sp500_universe)} stocks
• All 11 GICS Sectors Covered
• Complete Market Representation

**🔄 Professional Batch System**
NSE: Batch {st.session_state.nse_batch_num + 1}
S&P: Batch {st.session_state.sp500_batch_num + 1}

**💼 For Broking Associates**
Screenshot → Refresh → Next Batch
Zero Opportunity Missed!
""")

batch_size = st.sidebar.selectbox("Batch Size", [15, 20, 25, 30], index=1)

if st.sidebar.button("🔄 Reset Batch Counters"):
    st.session_state.nse_batch_num = 0
    st.session_state.sp500_batch_num = 0
    st.success("Batch counters reset - starting from batch 1")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📰 Market News", 
    f"🇮🇳 NSE Scanner ({len(nse_universe)} stocks)", 
    f"🇺🇸 S&P 500 Scanner ({len(sp500_universe)} stocks)", 
    "📊 Scan History"
])

# Tab 1: News
with tab1:
    st.subheader("📰 Market News & Analysis")
    
    if st.button("🔄 Refresh News") or not st.session_state.news_data:
        with st.spinner("Loading latest market news..."):
            st.session_state.news_data = fetch_news_optimized()
            st.success(f"Loaded {len(st.session_state.news_data)} news items!")
    
    if st.session_state.news_data:
        st.info(f"**📈 News Items: {len(st.session_state.news_data)}** | Last Updated: {datetime.now().strftime('%H:%M:%S')}")
        
        for news in st.session_state.news_data:
            impact_color = {'High': 'red', 'Medium': 'orange', 'Low': 'green'}[news['market_impact']]
            st.markdown(f"""
            <div class="news-item">
                <h4>{news['title']}</h4>
                <p><strong>Impact:</strong> <span style="color: {impact_color}">{news['market_impact']}</span> | 
                   <strong>Category:</strong> {news['category']}</p>
                <p>{news['summary']}</p>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                    <small>📅 {news['date']} | ⏰ {news['time']} | 📰 {news['source']}</small>
                    <a href="{news['link']}" target="_blank" style="background-color: #1f77b4; color:
            
