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
# Pure-Native Live Market Volume Analytics (No yfinance needed)
# --------------------------------------------------------
@st.cache_data(ttl=900)  # Cache market data for 15 minutes
def get_volume_breakout_metric_native(ticker):
    """
    Fetches historical daily volume data using a native web request layout
    to avoid compilation errors on experimental Python runtimes.
    """
    if ticker in ["ANFGF", "COPX"]: 
        return "N/A Volume", 0.0, "gray"
        
    try:
        # Use Yahoo's public chart endpoint via standard HTTP requests
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=30d&interval=1d"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return "Data Restricted", 0.0, "gray"
            
        json_data = response.json()
        volumes = json_data["chart"]["result"][0]["indicators"]["quote"][0]["volume"]
        
        # Filter out any potential null values from the endpoint array
        clean_volumes = [v for v in volumes if v is not None]
        
        if len(clean_volumes) < 20:
            return "No Volume Feed", 0.0, "gray"
            
        # 20-day historical average volume (excluding the most recent live day)
        avg_volume_20d = sum(clean_volumes[-21:-1]) / 20
        # Today's live trading volume
        live_volume = clean_volumes[-1]
        
        if avg_volume_20d == 0:
            return "0 Avg Vol", 0.0, "gray"
            
        pct_of_avg = (live_volume / avg_volume_20d) * 100
        color = "green" if pct_of_avg >= 100 else "red"
        
        return f"{pct_of_avg:.1f}% of 20D Avg", pct_of_avg, color
    except:
        return "Feed Offline", 0.0, "gray"

# --------------------------------------------------------
# 2. Hybrid Streamlit Data Pipeline
# --------------------------------------------------------
@st.cache_data(ttl=300)
def load_live_politician_data():
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
                if not ticker or ticker in ["N/A", "--", "NAN"] or len(ticker) > 5:
                    continue
                    
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
                    "Filing Date": parsed_date,
                    "Politician": str(row[name_col]).title() if name_col else "Unknown Lawmaker",
                    "Chamber": "Congress",
                    "Ticker": ticker,
                    "Type": tx_type,
                    "Amount Range": amt_str if amt_col else "Unknown",
                    "Numeric Max": numeric_max,
                    "Sector": data_store.SECTOR_MAP.get(ticker, "Other / Unclassified")
                })
                
            final_df = pd.DataFrame(cleaned_data)
            if not final_df.empty:
                return final_df.sort_values(by="Filing Date", ascending=False)
                
        return get_fallback_df()
    except:
        return get_fallback_df()

def get_fallback_df():
    df = pd.DataFrame(data_store.get_fallback_political_data())
    df["Filing Date"] = pd.to_datetime(df["Filing Date"])
    df["Sector"] = df["Ticker"].map(lambda x: data_store.SECTOR_MAP.get(x, "Other / Unclassified"))
    return df

def get_insider_data():
    df = pd.DataFrame(data_store.get_insider_data_raw())
    df["Sector"] = df["Ticker"].map(lambda x: data_store.SECTOR_MAP.get(x, "Other / Unclassified"))
    return df

def get_institutional_data():
    df = pd.DataFrame(data_store.get_institutional_data_raw())
    df["Sector"] = df["Ticker"].map(lambda x: data_store.SECTOR_MAP.get(x, "Other / Unclassified"))
    return df

df_insider_raw = get_insider_data()
df_poly_raw = load_live_politician_data()
df_inst_raw = get_institutional_data()
df_maga_raw = pd.DataFrame(data_store.get_maga_portfolio_data())

# --------------------------------------------------------
# 3. Sidebar Configuration & Aggregations
# --------------------------------------------------------
st.sidebar.header("🐋 Whale Order Filters")
min_insider_val = st.sidebar.slider("Minimum Insider Value ($)", 0, 1500000, 0, 50000)
min_poly_tier = st.sidebar.select_slider("Minimum Politician Tier", options=["All Trades", "$15k+", "$50k+", "$100k+", "$500k+"])
min_inst_val = st.sidebar.slider("Minimum Institutional Value ($M)", 0, 600, 20, 10) * 1000000

tier_mapping = {"All Trades": 0, "$15k+": 15000, "$50k+": 50000, "$100k+": 100000, "$500k+": 500000}

df_insider = df_insider_raw[df_insider_raw["Value ($)"].abs() >= min_insider_val]
df_poly = df_poly_raw[df_poly_raw["Numeric Max"] >= tier_mapping[min_poly_tier]]
df_inst = df_inst_raw[df_inst_raw["Value ($)"].abs() >= min_inst_val]

st.sidebar.write("---")
st.sidebar.subheader("📊 Combined Capital Hotspots")
combined_sectors = pd.concat([df_insider["Sector"], df_poly["Sector"], df_inst["Sector"]]).value_counts()
if not combined_sectors.empty:
    st.sidebar.bar_chart(combined_sectors)
else:
    st.sidebar.caption("No data matches parameters.")

# --------------------------------------------------------
# 4. Asymmetry Quad-Cross Reference Engine with Breakout Volume
# --------------------------------------------------------
insider_tickers = set(df_insider_raw["Ticker"].unique())
poly_tickers = set(df_poly_raw["Ticker"].unique())
inst_tickers = set(df_inst_raw["Ticker"].unique())
maga_tickers = set(df_maga_raw["Ticker"].unique())

# Core triple cross
triple_conviction = insider_tickers.intersection(poly_tickers).intersection(inst_tickers)

if triple_conviction:
    st.error("⚡ **Asymmetry Alert: Triple Conviction Breakout Matrix**")
    cols = st.columns(len(triple_conviction))
    for idx, ticker in enumerate(triple_conviction):
        with cols[idx]:
            c_actions = df_insider_raw[df_insider_raw["Ticker"] == ticker]
            p_actions = df_poly_raw[df_poly_raw["Ticker"] == ticker]
            i_actions = df_inst_raw[df_inst_raw["Ticker"] == ticker]
            
            maga_match = "🦅 MAGA Core Aligned" if ticker in maga_tickers else "Standard Coverage"
            
            # Fetch Volume using the native engine
            vol_label, vol_val, vol_color = get_volume_breakout_metric_native(ticker)
            
            with st.container(border=True):
                st.markdown(f"### **{ticker}**")
                st.caption(f"{data_store.SECTOR_MAP.get(ticker, 'General')} • {maga_match}")
                
                # Dynamic rendering based on native volume tracker calculations
                if vol_color == "green":
                    st.markdown(f"📈 **Live Volume:** :{vol_color}[{vol_label} 🔥 Breakout]")
                elif vol_color == "red":
                    st.markdown(f"📉 **Live Volume:** :{vol_color}[{vol_label}]")
                else:
                    st.markdown(f"⚪ **Live Volume:** {vol_label}")
                    
                st.markdown(f"**Corporate Insiders:** {len(c_actions)}  \n**Capitol Hill:** {len(p_actions)}  \n**Institutional Whales:** {len(i_actions)}")
    st.write("---")

# --------------------------------------------------------
# 5. Tab Viewports
# --------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🏢 Corporate Insiders", 
    "🏛️ Political Disclosures", 
    "🐋 Institutional Blocks",
    "🦅 MAGA Alpha Core"
])

with tab1:
    st.subheader("Form 4 Intelligence Feed")
    total_insider_buys = df_insider[df_insider["Value ($)"] > 0]["Value ($)"].sum()
    total_insider_sells = df_insider[df_insider["Value ($)"] < 0]["Value ($)"].sum()
    
    m1, m2 = st.columns(2)
    m1.metric("Total Tracked Buying Volume", f"${total_insider_buys:,.0f}")
    m2.metric("Total Tracked Selling Volume", f"${abs(total_insider_sells):,.0f}")
    
    st.dataframe(df_insider[["Filing Date", "Ticker", "Sector", "Insider", "Role", "Type", "Value ($)"]], hide_index=True, use_container_width=True)

with tab2:
    st.subheader("Live Capitol Hill Transactions")
    poly_purchases = df_poly[df_poly["Type"] == "🟢 Purchase"]["Numeric Max"].sum()
    poly_sales = df_poly[df_poly["Type"] == "🔴 Sale"]["Numeric Max"].sum()
    
    pm1, pm2 = st.columns(2)
    pm1.metric("Est. Lawmaker Inflow Capacity", f"${poly_purchases:,.0f}")
    pm2.metric("Est. Lawmaker Outflow Capacity", f"${poly_sales:,.0f}")
    
    ticker_search = st.text_input("🔍 Filter Disclosures by Stock Ticker", "").upper().strip()
    if ticker_search:
        df_poly = df_poly[df_poly["Ticker"] == ticker_search]
    
    if not df_poly.empty:
        display_poly = df_poly.copy()
        display_poly["Filing Date"] = display_poly["Filing Date"].dt.strftime('%Y-%m-%d')
        st.dataframe(display_poly[["Filing Date", "Politician", "Ticker", "Sector", "Type", "Amount Range"]], hide_index=True, use_container_width=True)
    else:
        st.warning("No data matching that filter layout.")

with tab3:
    st.subheader("Major Institutional Block Trade Changes")
    inst_inflow = df_inst[df_inst["Value ($)"] > 0]["Value ($)"].sum()
    inst_outflow = df_inst[df_inst["Value ($)"] < 0]["Value ($)"].sum()
    
    im1, im2 = st.columns(2)
    im1.metric("Whale Net Accumulation Blocks", f"${inst_inflow:,.0f}")
    im2.metric("Whale Net Distribution Blocks", f"${abs(inst_outflow):,.0f}")
    
    st.dataframe(df_inst[["Filing Date", "Ticker", "Sector", "Institution", "Type", "Shares Changed", "Value ($)"]], hide_index=True, use_container_width=True)

with tab4:
    st.subheader("🇺🇸 High-Conviction Federal Executive Tracker")
    st.caption("Aggregated tracking of core positions, recent rotation trends, and structural policy alignment plays.")
    
    df_maga = df_maga_raw.copy()
    df_maga["Sector"] = df_maga["Ticker"].map(lambda x: data_store.SECTOR_MAP.get(x, "Other / Unclassified"))
    
    mm1, mm2 = st.columns(2)
    mm1.metric("Est. Minimum Portfolio Allocation Tier", "$220,000,000")
    mm2.metric("Dominant Allocation Overweight", "Semiconductors / Infrastructure")
    
    st.write("---")
    st.dataframe(df_maga[["Ticker", "Sector", "Holding Tier", "Estimated Value", "Action", "Thesis"]], hide_index=True, use_container_width=True)
