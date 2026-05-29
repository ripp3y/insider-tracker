import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sec_api import QueryApi
import yfinance as yf
import json
import os

# ──────────────────────────────────────────────────────────
# CONFIGURATION & GLOBAL SETUP (PERSISTENT CORES)
# ──────────────────────────────────────────────────────────
st.set_page_config(page_title="Asymmetry Dashboard", layout="wide")

WATCHLIST_FILE = "watchlist.json"
BASE_SEED_TRACKS = [
    "FIX", "VRT", "CIEN", "SMCI", "BE", 
    "NVDA", "MRVL", "TSM", "UMC", "POWL", "AGX",
    "STX", "COPX", "ANFGF", "ALB", "REMX", "DVN"
]

def load_permanent_watchlist():
    """Reads saved tickers from the local JSON storage file."""
    if os.path.exists(WATCHLIST_FILE):
        try:
            with open(WATCHLIST_FILE, "r") as f:
                saved_list = json.load(f)
                if isinstance(saved_list, list) and len(saved_list) > 0:
                    return saved_list
        except Exception:
            pass
    return BASE_SEED_TRACKS.copy()

def save_permanent_watchlist(updated_list):
    """Commits active tracking state directly to disk memory."""
    try:
        with open(WATCHLIST_FILE, "w") as f:
            json.dump(updated_list, f, indent=4)
    except Exception as e:
        st.sidebar.error(f"Memory Write Failure: {e}")

# Initialize session state from the permanent file matrix
if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_permanent_watchlist()

# Load SEC API Key from Streamlit Secrets securely
SEC_API_KEY = st.secrets.get("SEC_API_KEY", "")

# ──────────────────────────────────────────────────────────
# SIDEBAR CONTROLS & DYNAMIC WATCHLIST MANAGER
# ──────────────────────────────────────────────────────────
st.sidebar.title("🦅 Asymmetry Control Panel")

if not SEC_API_KEY:
    SEC_API_KEY = st.sidebar.text_input("Enter SEC-API.io Key:", type="password")
else:
    st.sidebar.success("🔑 SEC Connection Authenticated.")

if not SEC_API_KEY:
    st.warning("⚠️ Please provide your SEC-API.io key in the sidebar or Cloud Secrets to run the terminal components.")
    st.stop()

lookback_days = st.sidebar.slider("Insider Tracking Window (Days)", min_value=3, max_value=30, value=14)

st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Watchlist Asset Matrix")

# 1. Bulk Add Tickers Interface
bulk_input = st.sidebar.text_input("Add New Ticker(s) (Comma Separated):", placeholder="e.g., DRAM, AXTI, MTZ, SOXX")
if st.sidebar.button("➕ Inject into Matrix"):
    if bulk_input:
        new_tickers = [t.strip().upper() for t in bulk_input.split(",") if t.strip()]
        added_count = 0
        for ticker in new_tickers:
            if ticker not in st.session_state.watchlist:
                st.session_state.watchlist.append(ticker)
                added_count += 1
        if added_count > 0:
            save_permanent_watchlist(st.session_state.watchlist)
            st.sidebar.success(f"Injected {added_count} new asset tracks!")
            st.rerun()

# 2. Individual Removal Interface
ticker_to_remove = st.sidebar.selectbox("Select Asset to Purge:", [""] + sorted(st.session_state.watchlist))
if st.sidebar.button("❌ Remove Selected"):
    if ticker_to_remove and ticker_to_remove in st.session_state.watchlist:
        st.session_state.watchlist.remove(ticker_to_remove)
        save_permanent_watchlist(st.session_state.watchlist)
        st.sidebar.warning(f"Purged {ticker_to_remove} from tracking matrix.")
        st.rerun()

st.sidebar.info(f"Total Active Trackers: **{len(st.session_state.watchlist)}**")

# ──────────────────────────────────────────────────────────
# THREE-TAB LAYOUT (ADDED LIVE INSTITUTIONAL ANALYSIS)
# ──────────────────────────────────────────────────────────
tab_insider, tab_radar, tab_institutional = st.tabs([
    "🕵️‍♂️ Live C-Suite Insiders", 
    "📈 Structural Uptrend Radar", 
    "🐳 Institutional Distribution"
])

query_api = QueryApi(api_key=SEC_API_KEY)

# ──────────────────────────────────────────────────────────
# DATA FETCHING UTILITY ENGINE
# ──────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def fetch_raw_market_data(ticker_list):
    """Unified engine to batch load market rows cleanly."""
    if not ticker_list:
        return {}
    
    tickers_string = " ".join(ticker_list)
    try:
        batch_data = yf.download(tickers_string, period="1y", group_by="ticker", threads=False, progress=False)
    except Exception:
        batch_data = pd.DataFrame()
        
    master_frames = {}
    for ticker in ticker_list:
        df = pd.DataFrame()
        if not batch_data.empty and len(ticker_list) > 1 and ticker in batch_data.columns.levels[0]:
            df = batch_data[ticker].dropna()
        elif not batch_data.empty and len(ticker_list) == 1:
            df = batch_data.dropna()
            
        if df.empty or len(df) < 5:
            try:
                asset = yf.Ticker(ticker)
                df = asset.history(period="1y").dropna()
            except Exception:
                continue
        if not df.empty and len(df) >= 5:
            master_frames[ticker] = df
            
    return master_frames

# ──────────────────────────────────────────────────────────
# TAB 1: INSIDER TRADING LOGIC
# ──────────────────────────────────────────────────────────
with tab_insider:
    st.subheader("Real-Time Corporate Insider Outlays")
    st.markdown("Scraping direct SEC EDGAR Form 4 streams. Automated robotic 10b51 plans are completely omitted.")
    
    @st.cache_data(ttl=300)
    def fetch_high_conviction_insiders(days_to_search):
        start_date = (datetime.now() - timedelta(days=days_to_search)).strftime('%Y-%m-%d')
        lucene_query = (
            f"formType:\"4\" AND "
            f"filedAt:[{start_date} TO *] AND "
            f"transactions.transactionCode:\"P\" AND "
            f"transactions.isRule10b51:\"false\""
        )
        payload = {
            "query": { "query_string": { "query": lucene_query } },
            "from": "0", "size": "50",
            "sort": [{ "filedAt": { "order": "desc" } }]
        }
        try:
            response = query_api.get_filings(payload)
            filings = response.get("filings", [])
            parsed_trades = []
            for filing in filings:
                issuer = filing.get("issuer", {})
                if not issuer: continue
                ticker = issuer.get("tradingSymbol", "N/A")
                company_name = issuer.get("name", "N/A")
                reporting_owner = filing.get("reportingOwner", {})
                insider_name = reporting_owner.get("name", "N/A") if reporting_owner else "N/A"
                
                role = "Other"
                if reporting_owner:
                    is_director = reporting_owner.get("isDirector", False)
                    is_officer = reporting_owner.get("isOfficer", False)
                    officer_title = reporting_owner.get("officerTitle", "")
                    if "CEO" in str(officer_title).upper(): role = "CEO"
                    elif is_officer: role = f"Officer ({officer_title})" if officer_title else "Officer"
                    elif is_director: role = "Director"

                for tx in filing.get("nonDerivativeTransactions", []):
                    if tx.get("transactionCode") == "P" and str(tx.get("isRule10b51")).lower() != "true":
                        shares = float(tx.get("transactionShares", 0) or 0)
                        price = float(tx.get("transactionPricePerShare", 0) or 0)
                        total_value = shares * price
                        shares_owned_after = float(tx.get("sharesOwnedFollowingTransaction", 0) or 0)
                        
                        position_increase_pct = 0
                        if (shares_owned_after - shares) > 0:
                            position_increase_pct = (shares / (shares_owned_after - shares)) * 100

                        if total_value >= 10000:
                            parsed_trades.append({
                                "Filing Date": filing.get("filedAt")[:10] if filing.get("filedAt") else "N/A",
                                "Ticker": ticker,
                                "Company Name": company_name,
                                "Insider Trader": insider_name,
                                "Role": role,
                                "Shares Bought": f"{shares:,.0f}",
                                "Price Paid": f"${price:,.2f}",
                                "Total Outlay": total_value,
                                "Position Jump": f"+{position_increase_pct:.1f}%" if shares_owned_after else "New Stake"
                            })
            df = pd.DataFrame(parsed_trades)
            return df.sort_values(by="Total Outlay", ascending=False).reset_index(drop=True) if not df.empty else pd.DataFrame()
        except Exception as e:
            st.error(f"SEC Query Engine Error: {e}")
            return pd.DataFrame()

    with st.spinner("Extracting SEC filings..."):
        insider_df = fetch_high_conviction_insiders(lookback_days)

    if not insider_df.empty:
        cluster_counts = insider_df.groupby("Ticker")["Insider Trader"].nunique()
        clusters = cluster_counts[cluster_counts >= 2].index.tolist()
        if clusters:
            st.error(f"### 🚨 MULTI-INSIDER CLUSTERS SPOTTED: {', '.join(clusters)}")
        
        display_insider = insider_df.copy()
        display_insider["Total Outlay"] = display_insider["Total Outlay"].apply(lambda x: f"${x:,.2f}")
        st.dataframe(display_insider, use_container_width=True)
    else:
        st.info("No manual cash purchases detected over $10k in this timeframe.")

# ──────────────────────────────────────────────────────────
# TAB 2: STRUCTURAL UPTREND RADAR (PERSISTENT DATA TRACKS)
# ──────────────────────────────────────────────────────────
with tab_radar:
    st.subheader("Master Matrix Trend Architecture")
    st.markdown("Filtered for immediate 20-day momentum. Handles recently debuted assets and IPO allocations automatically.")
    
    if st.button("🔄 Execute Hardened Matrix Scan"):
        with st.spinner("Compiling multi-timeframe structural trends..."):
            market_data = fetch_raw_market_data(st.session_state.watchlist)
            screened_data = []
            
            for ticker, df in market_data.items():
                try:
                    close_col = 'Close' if 'Close' in df.columns else '4. close'
                    vol_col = 'Volume' if 'Volume' in df.columns else '5. volume'
                    
                    close_series = df[close_col].astype(float)
                    vol_series = df[vol_col].astype(float)
                    
                    current_price = float(close_series.iloc[-1])
                    available_bars = len(close_series)
                    
                    current_volume = float(vol_series.iloc[-1])
                    vol_lookback = min(20, available_bars)
                    avg_volume_baseline = float(vol_series.rolling(window=vol_lookback).mean().iloc[-1])
                    
                    volume_surge_pct = 0.0
                    if avg_volume_baseline > 0:
                        volume_surge_pct = ((current_volume - avg_volume_baseline) / avg_volume_baseline) * 100
                    
                    rsi_lookback = min(14, available_bars - 1)
                    if rsi_lookback >= 2:
                        delta = close_series.diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_lookback).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_lookback).mean()
                        rs = gain / (loss + 1e-9)
                        rsi = float(100 - (100 / (1 + rs)).iloc[-1])
                    else:
                        rsi = 50.0

                    perf_lookback = min(21, available_bars)
                    price_past = float(close_series.iloc[-perf_lookback])
                    perf_1m = ((current_price - price_past) / price_past) * 100

                    if available_bars < 50:
                        sma_short = float(close_series.rolling(window=min(10, available_bars)).mean().iloc[-1])
                        sma_long = float(close_series.rolling(window=min(20, available_bars)).mean().iloc[-1])
                        
                        if current_price > sma_short and sma_short > sma_long: status = "🔥 Strong Uptrend"
                        elif current_price <= sma_short and current_price > sma_long: status = "💤 Stalling / Flat"
                        else: status = "⚠️ Structural Breakdown"
                        
                        display_50, dist_to_50_str, display_200, dist_to_200_str = "N/A (New)", "0.0%", "N/A (New)", "0.0%"
                    else:
                        sma_20 = float(close_series.rolling(window=20).mean().iloc[-1])
                        sma_50 = float(close_series.rolling(window=50).mean().iloc[-1])
                        sma_200 = float(close_series.rolling(window=200).mean().iloc[-1]) if available_bars >= 200 else sma_50
                        
                        if current_price > sma_20 and sma_20 > sma_50 and sma_50 > sma_200: status = "🔥 Strong Uptrend"
                        elif current_price <= sma_20 and current_price > sma_50: status = "💤 Stalling / Flat"
                        elif current_price <= sma_50 and current_price > sma_200: status = "⏳ Support Test"
                        else: status = "⚠️ Structural Breakdown"
                            
                        dist_to_50 = ((current_price - sma_50) / sma_50) * 100
                        display_50 = f"${sma_50:.2f}"
                        dist_to_50_str = f"{dist_to_50:+.1f}%"
                        
                        if available_bars >= 200:
                            dist_to_200 = ((current_price - sma_200) / sma_200) * 100
                            display_200 = f"${sma_200:.2f}"
                            dist_to_200_str = f"{dist_to_200:+.1f}%"
                        else:
                            display_200, dist_to_200_str = "N/A", "0.0%"

                    screened_data.append({
                        "Ticker": ticker, "Price": f"${current_price:.2f}", "Structure": status,
                        "RSI (14)": f"{rsi:.1f}", "1-Mo Return": f"{perf_1m:+.1f}%", "Vol Surge (20D MA)": f"{volume_surge_pct:+.1f}%",
                        "SMA 50 Support": display_50, "Dist to SMA 50": dist_to_50_str, "SMA 200 Floor": display_200,
                        "Dist to SMA 200": dist_to_200_str, "raw_sort": perf_1m
                    })
                except Exception:
                    pass

        if screened_data:
            radar_df = pd.DataFrame(screened_data).sort_values(by="raw_sort", ascending=False).drop(columns=["raw_sort"]).reset_index(drop=True)
            def style_structure_rows(val):
                if "🔥" in str(val): return "background-color: rgba(40, 167, 69, 0.15);"
                elif "💤" in str(val): return "background-color: rgba(255, 140, 0, 0.15);"
                elif "⏳" in str(val): return "background-color: rgba(255, 193, 7, 0.15);"
                elif "⚠️" in str(val): return "background-color: rgba(220, 53, 69, 0.15);"
                return ""
            st.dataframe(radar_df.style.map(style_structure_rows, subset=["Structure"]), use_container_width=True, hide_index=True)
        else:
            st.info("The watchlist is empty or data servers are congested. Load tickers to ignite.")

# ──────────────────────────────────────────────────────────
# TAB 3: LIVE INSTITUTIONAL DISTRIBUTION ENGINE (NEW TAB)
# ──────────────────────────────────────────────────────────
with tab_institutional:
    st.subheader("Institutional Whales Tracking Matrix")
    st.markdown("Isolates anomalous trading footprint trends. Identifies heavy institutional loading vs. aggressive retail distribution distribution.")
    
    if st.button("🐳 Run Whales Volume Footprint Scan"):
        with st.spinner("Decoding institutional block setups..."):
            market_data = fetch_raw_market_data(st.session_state.watchlist)
            whale_data = []
            
            for ticker, df in market_data.items():
                try:
                    close_col = 'Close' if 'Close' in df.columns else '4. close'
                    vol_col = 'Volume' if 'Volume' in df.columns else '5. volume'
                    open_col = 'Open' if 'Open' in df.columns else '1. open'
                    
                    close_series = df[close_col].astype(float)
                    vol_series = df[vol_col].astype(float)
                    open_series = df[open_col].astype(float)
                    
                    current_price = float(close_series.iloc[-1])
                    prev_price = float(close_series.iloc[-2])
                    current_open = float(open_series.iloc[-1])
                    current_volume = float(vol_series.iloc[-1])
                    
                    available_bars = len(close_series)
                    vol_lookback = min(20, available_bars)
                    avg_volume_20d = float(vol_series.rolling(window=vol_lookback).mean().iloc[-1])
                    
                    # 1. Volume Delta Matrix
                    vol_surge_pct = ((current_volume - avg_volume_20d) / avg_volume_20d) * 100 if avg_volume_20d > 0 else 0.0
                    
                    # 2. Contextual Footprint Scoring Logic
                    price_change_pct = ((current_price - prev_price) / prev_price) * 100
                    intraday_direction = current_price - current_open
                    
                    # Classify if volume spike indicates loading or unloading
                    if price_change_pct > 0 and intraday_direction > 0:
                        flow_type = "🐋 Institutional Accumulation"
                        sort_score = vol_surge_pct  # Highest buying surge stays at top
                    elif price_change_pct < 0 and intraday_direction < 0:
                        flow_type = "🚨 Heavy Distribution"
                        sort_score = vol_surge_pct * 2  # Penalize heavy drops higher to force focus
                    else:
                        flow_type = "💨 Mixed / Light Retail"
                        sort_score = -500.0 + vol_surge_pct

                    # Compute RSI 14
                    rsi_lookback = min(14, available_bars - 1)
                    if rsi_lookback >= 2:
                        delta = close_series.diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_lookback).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_lookback).mean()
                        rs = gain / (loss + 1e-9)
                        rsi = float(100 - (100 / (1 + rs)).iloc[-1])
                    else:
                        rsi = 50.0

                    whale_data.append({
                        "Ticker": ticker,
                        "Price": f"${current_price:.2f}",
                        "Net Change": f"{price_change_pct:+.2f}%",
                        "Whale Flow Status": flow_type,
                        "Vol Surge (20D MA)": f"{vol_surge_pct:+.1f}%",
                        "RSI (14)": f"{rsi:.1f}",
                        "raw_sort": sort_score
                    })
                except Exception:
                    pass

        if whale_data:
            whale_df = pd.DataFrame(whale_data).sort_values(by="raw_sort", ascending=False).drop(columns=["raw_sort"]).reset_index(drop=True)
            
            def style_whale_rows(val):
                if "🐋" in str(val): return "background-color: rgba(40, 167, 69, 0.15);"  # Emerald loading
                elif "🚨" in str(val): return "background-color: rgba(220, 53, 69, 0.15);"  # Crimson selling
                return ""

            st.dataframe(
                whale_df.style.map(style_whale_rows, subset=["Whale Flow Status"]),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Load tickers in your active list and fire the footprint scanner.")
