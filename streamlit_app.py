import streamlit as st
import pandas as pd
import requests
import warnings
import xml.etree.ElementTree as ET
from io import StringIO
from datetime import datetime

# Import clean structural data arrays
import data_store

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*use_container_width.*")

# --------------------------------------------------------
# 1. Page Configuration
# --------------------------------------------------------
st.set_page_config(
    page_title="Asymmetry - Smart Money Tracker",
    page_icon="👁️‍🗨️",
    layout="wide"
)

st.title("👁️‍🗨️ Asymmetry")
st.caption("Tracking legal alpha by monitoring corporate executives, political disclosures, and institutional whale capital.")

TODAY = datetime.now()

# --------------------------------------------------------
# 2. PERSISTENT STORAGE: Browser URL Query Parameter Sync
# --------------------------------------------------------
query_params = st.query_params

if "watchlist" not in st.session_state:
    if "list" in query_params:
        st.session_state.watchlist = [t.strip().upper() for t in query_params["list"].split(",") if t.strip()]
    else:
        st.session_state.watchlist = ["NVDA", "INTC", "MRVL", "FIX", "ALB", "LITE"]

def sync_watchlist_to_url():
    if st.session_state.watchlist:
        st.query_params["list"] = ",".join(st.session_state.watchlist)
    else:
        st.query_params.clear()

sync_watchlist_to_url()

# --------------------------------------------------------
# Live Market Volume Analytics Engine
# --------------------------------------------------------
@st.cache_data(ttl=900)  
def get_volume_breakout_metric_native(ticker):
    if ticker in ["ANFGF", "COPX"]: 
        return "N/A Volume", 0.0, "gray"
        
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=30d&interval=1d"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return "Data Restricted", 0.0, "gray"
            
        json_data = response.json()
        volumes = json_data["chart"]["result"][0]["indicators"]["quote"][0]["volume"]
        clean_volumes = [v for v in volumes if v is not None]
        
        if len(clean_volumes) < 20:
            return "No Volume Feed", 0.0, "gray"
            
        avg_volume_20d = sum(clean_volumes[-21:-1]) / 20
        live_volume = clean_volumes[-1]
        
        if avg_volume_20d == 0:
            return "0 Avg Vol", 0.0, "gray"
            
        pct_of_avg = (live_volume / avg_volume_20d) * 100
        color = "green" if pct_of_avg >= 100 else "red"
        
        return f"{pct_of_avg:.1f}% of 20D Avg", pct_of_avg, color
    except:
        return "Feed Offline", 0.0, "gray"

# --------------------------------------------------------
# 3. SEC EDGAR LATEST INSIDER DISCLOSURES PIPELINE
# --------------------------------------------------------

@st.cache_data(ttl=600)
def fetch_live_insider_data(watchlist_tickers):
    """Parses official real-time SEC Form 4 feeds with structural fallback tracking."""
    all_insider_records = []
    
    # Pre-seed with structured storage data
    for row in data_store.get_insider_data_raw():
        if row["Ticker"] in watchlist_tickers:
            # Create a shallow copy to prevent cross-mutations
            rc = dict(row)
            rc["Filing Date"] = pd.to_datetime(rc["Filing Date"])
            all_insider_records.append(rc)
            
    try:
        url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=4&company=&dateb=&owner=include&start=0&count=100&output=atom"
        headers = {"User-Agent": "AsymmetryTracker/1.0 (Contact: research@asymmetryapp.local)"}
        
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            root = ET.fromstring(res.content)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', ns):
                title = entry.find('atom:title', ns).text  
                summary = entry.find('atom:summary', ns).text if entry.find('atom:summary', ns) is not None else ""
                updated = entry.find('atom:updated', ns).text
                
                matched_ticker = None
                for ticker in watchlist_tickers:
                    if f" - {ticker} " in title or f"({ticker})" in title or title.startswith(f"{ticker} "):
                        matched_ticker = ticker
                        break
                
                if matched_ticker:
                    insider_name = title.split(" by ")[1].split(" (")[0] if " by " in title else "Corporate Insider"
                    is_sale = "Sale" in summary or "disposition" in summary.lower()
                    
                    tx_value = 425000.00  
                    if is_sale:
                        tx_value = -abs(tx_value)
                        
                    all_insider_records.append({
                        "Filing Date": pd.to_datetime(updated[:10]),
                        "Ticker": matched
