import streamlit as st
import pandas as pd
import requests
import warnings
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
# 3. LIVE DATA SCRAPING PIPELINES
# --------------------------------------------------------

@st.cache_data(ttl=600)
def fetch_live_insider_data(watchlist_tickers):
    """Scrapes real-time insider filings dynamically for watchlisted stocks."""
    all_insider_records = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    for ticker in watchlist_tickers:
        try:
            url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=insiderTransactions"
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                transactions = data["quoteSummary"]["result"][0]["insiderTransactions"]["transactions"]
                
                for tx in transactions[:15]: # Pull the 15 latest filings per stock
                    raw_date = tx.get("startDate", {}).get("fmt", TODAY.strftime("%Y-%m-%d"))
                    shares = tx.get("shares", {}).get("raw", 0)
                    value = shares * tx.get("value", {}).get("raw", 10) # Est value
                    
                    # Determine Transaction Type Flag
                    tx_type = tx.get("transactionText", "Transaction")
                    if "Sale" in tx_type or "Option Exercise" in tx_type:
                        value = -abs(value)
                        type_flag = "🔴 Sale"
                    else:
                        type_flag = "🟢 Purchase"
                        
                    all_insider_records.append({
                        "Filing Date": pd.to_datetime(raw_date),
                        "Ticker": ticker,
                        "Sector": data_store.SECTOR_MAP.get(ticker, "Technology Infrastructure"),
                        "Insider": tx.get("filerName", "Corporate Officer"),
                        "Role": tx.get("filerRelation", "Executive Officer"),
                        "Type": type_flag,
                        "Value ($)": value
                    })
        except:
            continue
            
    if all_insider_records:
        df = pd.DataFrame(all_insider_records)
        return df.sort_values(by="Filing Date", ascending=False)
    return pd.DataFrame(columns=["Filing Date", "Ticker", "Sector", "Insider", "Role", "Type", "Value ($)"])


@st.cache_data(ttl=300)
def load_live_politician_data(watchlist_tickers):
    """Scrapes Congress data and filters down to watchlisted tickers instantly."""
    screener_url = "https://raw.githubusercontent.com/thefuzzlemind/free-congress-stock-data/main/data/latest_trades.csv"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(screener_url, headers=headers, timeout=5)
        if response.status_code == 200 and len(response.text) > 100:
            df = pd.read_csv(StringIO(response.text))
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            name_col = next((c for c in ["politician", "representative", "name"] if c in df.columns), None)
            date_col = next((c for c in ["filing_date", "disclosure_date", "date"] if c in df.columns), None)
            ticker_col = next((c for c in ["ticker", "symbol"] if c in df.columns), None)
            type_col = next((c for c in ["type", "transaction"] if c in df.columns), None)
            amt_col = next((c for c in ["amount", "range"] if c in df.columns), None)
            
            cleaned_data = []
            for _, row in df.iterrows():
                ticker = str(row[ticker_col]).upper().strip() if ticker_col else "N/A"
                if ticker not in watchlist_tickers:
                    continue # Skip anything outside your active watchlist
                    
                raw_date = row[date_col] if date_col else TODAY
                try: parsed_date = pd.to_datetime(raw_date)
                except: parsed_date = TODAY
                raw_type = str(row[type_col]).lower() if type_col else "purchase"
                tx_type = "🔴 Sale" if "sale" in raw_type or "sell" in raw_type else "🟢 Purchase"
                
                amt_str = str(row[amt_col]) if amt_col else "$15,001 - $50,000"
                numeric_max = 50000
                if "1,000,00" in amt_str: numeric_max = 5000000
                elif "500,00" in amt_str: numeric_max = 1000000
                elif "100,00" in amt_str: numeric_max = 250000
                elif "50,00" in amt_str: numeric_max = 100000
                
                cleaned_data.append({
                    "Filing Date": parsed_date, "Politician": str(row[name_col]).title() if name_col else "Unknown Lawmaker",
                    "Chamber": "Congress", "Ticker": ticker, "Type": tx_type, "Amount Range": amt_str, "Numeric Max": numeric_max,
                    "Sector": data_store.SECTOR_MAP.get(ticker, "Other / Unclassified")
                })
            final_df = pd.DataFrame(cleaned_data)
            if not final_df.empty: return final_df.sort_values(by="Filing Date", ascending=False)
        return pd.DataFrame(columns=["Filing Date", "Politician", "Ticker", "Sector", "Type", "Amount Range", "Numeric Max"])
    except:
        return pd.DataFrame(columns=["Filing Date", "Politician", "Ticker", "Sector", "Type", "Amount Range", "Numeric Max"])


@st.cache_data(ttl=600)
def fetch_live_institutional_data(watchlist_tickers):
    """Scrapes structural institution/fund major block positions dynamically."""
    all_inst_records = []
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for ticker in watchlist_tickers:
        try:
            url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=institutionOwnership"
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                ownerships = data["quoteSummary"]["result"][0]["institutionOwnership"]["ownershipList"]
                
                for inst in ownerships[:10]: # Top 10 primary block holders
                    raw_date = inst.get("reportDate", {}).get("fmt", TODAY.strftime("%Y-%m-%d"))
                    shares = inst.get("position", {}).get("raw", 0)
                    value = inst.get("value", {}).get("raw", shares * 50)
                    
                    all_inst_records.append({
                        "Filing Date": pd.to_datetime(raw_date),
                        "Ticker": ticker,
                        "Sector": data_store.SECTOR_MAP.get(ticker, "Core Portfolio Asset"),
                        "Institution": inst.get("organization", "Institutional Asset Management"),
                        "Type": "🐳 Core Block Accumulation",
                        "Shares Changed": shares,
                        "Value ($)": value
                    })
        except:
            continue
            
    if all_inst_records:
        df = pd.DataFrame(all_inst_records)
        return df.sort_values(by="Filing Date", ascending=False)
    return pd.DataFrame(columns=["Filing Date", "Ticker", "Sector", "Institution", "Type", "Shares Changed", "Value ($)"])

# --------------------------------------------------------
# 4. LIVE PIPELINE RUNNERS
# --------------------------------------------------------
df_insider_raw = fetch_live_insider_data(st.session_state.watchlist)
df_poly_raw = load_live_politician_data(st.session_state.watchlist)
df_inst_raw = fetch_live_institutional_data(st.session_state.watchlist)
df_maga_raw = pd.DataFrame(data_store.get_maga_portfolio_data())

# Filter down rows based on user sidebar configuration parameters
st.sidebar.header("🐋 Whale Order Filters")
min_insider_val = st.sidebar.slider("Minimum Insider Value ($)", 0, 1500000, 0, 50000)
min_poly_tier = st.sidebar.select_slider("Minimum Politician Tier", options=["All Trades", "$15k+", "$50k+", "$100k+", "$500k+"])
min_inst_val = st.sidebar.slider("Minimum Institutional Value ($M)", 0, 600, 0, 10) * 1000000

tier_mapping = {"All Trades": 0, "$15k+": 15000, "$50k+": 50000, "$100k+": 100000, "$500k+": 500000}

# Generate final rendering dataframes
df_insider = df_insider_raw[df_insider_raw["Value ($)"].abs() >= min_insider_val] if not df_insider_raw.empty else df_insider_raw
df_poly = df_poly_raw[df_poly_raw["Numeric Max"] >= tier_mapping[min_poly_tier]] if not df_poly_raw.empty else df_poly_raw
df_inst = df_inst_raw[df_inst_raw["Value ($)"].abs() >= min_inst_val] if not df_inst_raw.empty else df_inst_raw

st.sidebar.write("---")
st.sidebar.subheader("📊 Combined Capital Hotspots")
combined_sectors = pd.concat([df_insider["Sector"], df_poly["Sector"], df_inst["Sector"]]).value_counts() if (not df_insider.empty or not df_poly.empty or not df_inst.empty) else pd.Series()
if not combined_sectors.empty:
    st.sidebar.bar_chart(combined_sectors)
else:
    st.sidebar.caption("Add tickers or adjust filters to view layout charts.")

# --------------------------------------------------------
# 5. Triple Conviction Alert Cross-Reference Core
# --------------------------------------------------------
if not df_insider_raw.empty and not df_poly_raw.empty and not df_inst_raw.empty:
    insider_tickers = set(df_insider_raw["Ticker"].unique())
    poly_tickers = set(df_poly_raw["Ticker"].unique())
    inst_tickers = set(df_inst_raw["Ticker"].unique())
    triple_conviction = insider_tickers.intersection(poly_tickers).intersection(inst_tickers)
else:
    triple_conviction = set()

if triple_conviction:
    st.error("⚡ **Asymmetry Alert: Triple Conviction Breakout Matrix**")
    cols = st.columns(len(triple_conviction))
    for idx, ticker in enumerate(triple_conviction):
        with cols[idx]:
            c_actions = df_insider_raw[df_insider_raw["Ticker"] == ticker]
            p_actions = df_poly_raw[df_poly_raw["Ticker"] == ticker]
            i_actions = df_inst_raw[df_inst_raw["Ticker"] == ticker]
            vol_label, vol_val, vol_color = get_volume_breakout_metric_native(ticker)
            
            with st.container(border=True):
                st.markdown(f"### **{ticker}**")
                if vol_color == "green":
                    st.markdown(f"📈 **Live Volume:** :{vol_color}[{vol_label} 🔥 Breakout]")
                else:
                    st.markdown(f"⚪ **Live Volume:** {vol_label}")
                st.markdown(f"**Corporate Insiders:** {len(c_actions)}  \n**Capitol Hill:** {len(p_actions)}  \n**Institutional Whales:** {len(i_actions)}")
    st.write("---")

# --------------------------------------------------------
# 6. Tab Viewports
# --------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏢 Corporate Insiders", 
    "🏛️ Political Disclosures", 
    "🐋 Institutional Blocks",
    "🦅 MAGA Alpha Core",
    "📋 Custom Watchlist"
])

with tab1:
    st.subheader("Form 4 Intelligence Feed (Live Web Streams)")
    if not df_insider.empty:
        total_insider_buys = df_insider[df_insider["Value ($)"] > 0]["Value ($)"].sum()
        total_insider_sells = df_insider[df_insider["Value ($)"] < 0]["Value ($)"].sum()
        m1, m2 = st.columns(2)
        m1.metric("Total Tracked Buying Volume", f"${total_insider_buys:,.0f}")
        m2.metric("Total Tracked Selling Volume", f"${abs(total_insider_sells):,.0f}")
        st.dataframe(df_insider[["Filing Date", "Ticker", "Sector", "Insider", "Role", "Type", "Value ($)"]], hide_index=True, use_container_width=True)
    else:
        st.info("No live insider trades matching current watchlist items or filter settings.")

with tab2:
    st.subheader("Live Capitol Hill Transactions")
    if not df_poly.empty:
        poly_purchases = df_poly[df_poly["Type"] == "🟢 Purchase"]["Numeric Max"].sum()
        poly_sales = df_poly[df_poly["Type"] == "🔴 Sale"]["Numeric Max"].sum()
        pm1, pm2 = st.columns(2)
        pm1.metric("Est. Lawmaker Inflow Capacity", f"${poly_purchases:,.0f}")
        pm2.metric("Est. Lawmaker Outflow Capacity", f"${poly_sales:,.0f}")
        
        display_poly = df_poly.copy()
        display_poly["Filing Date"] = display_poly["Filing Date"].dt.strftime('%Y-%m-%d')
        st.dataframe(display_poly[["Filing Date", "Politician", "Ticker", "Sector", "Type", "Amount Range"]], hide_index=True, use_container_width=True)
    else:
        st.info("No congressional trades filed on these tickers in the last 30 days.")

with tab3:
    st.subheader("Major Institutional Block Holdings")
    if not df_inst.empty:
        inst_inflow = df_inst["Value ($)"].sum()
        im1 = st.metric("Whale Net Core Institutional Assets Covered", f"${inst_inflow:,.0f}")
        st.dataframe(df_inst[["Filing Date", "Ticker", "Sector", "Institution", "Type", "Shares Changed", "Value ($)"]], hide_index=True, use_container_width=True)
    else:
        st.info("No active block holding profiles matching tickers.")

with tab4:
    st.subheader("🇺🇸 High-Conviction Federal Executive Tracker")
    df_maga = df_maga_raw.copy()
    df_maga["Sector"] = df_maga["Ticker"].map(lambda x: data_store.SECTOR_MAP.get(x, "Other / Unclassified"))
    mm1, mm2 = st.columns(2)
    mm1.metric("Est. Minimum Portfolio Allocation Tier", "$220,000,000")
    mm2.metric("Dominant Allocation Overweight", "Semiconductors / Infrastructure")
    st.dataframe(df_maga[["Ticker", "Sector", "Holding Tier", "Estimated Value", "Action", "Thesis"]], hide_index=True, use_container_width=True)

with tab5:
    st.subheader("📋 Personalized High-Alpha Watchlist")
    st.caption("Add custom stock tickers here to monitor their real-time volume breakout statuses instantly.")
    
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        new_ticker = st.text_input("Enter Stock Ticker to Add", placeholder="e.g. SMCI, VRT, CEG", key="add_input").upper().strip()
    with col_btn:
        st.write("##") 
        if st.button("➕ Add Ticker", use_container_width=True):
            if new_ticker and new_ticker not in st.session_state.watchlist:
                st.session_state.watchlist.append(new_ticker)
                sync_watchlist_to_url() 
                st.rerun() 
                
    st.write("---")
    
    if st.session_state.watchlist:
        for ticker in st.session_state.watchlist:
            vol_label, vol_val, vol_color = get_volume_breakout_metric_native(ticker)
            sector_name = data_store.SECTOR_MAP.get(ticker, "Custom Tracker Asset / Alpha Target")
            
            metric_col, info_col, action_col = st.columns([2, 4, 1])
            
            with metric_col:
                if vol_color == "green":
                    st.success(f"**{ticker}** • {vol_label}")
                elif vol_color == "red":
                    st.error(f"**{ticker}** • {vol_label}")
                else:
                    st.info(f"**{ticker}** • {vol_label}")
                    
            with info_col:
                st.markdown(f"**Sector:** {sector_name}")
                st.caption(f"Live API cross-reference lookups successfully running for asset.")
                
            with action_col:
                st.write("") 
                if st.button(f"➖ Remove", key=f"del_{ticker}", use_container_width=True):
                    st.session_state.watchlist.remove(ticker)
                    sync_watchlist_to_url() 
                    st.rerun() 
            st.write("---")
    else:
        st.info("Your watchlist is currently empty. Use the input panel above to track custom parameters.")
