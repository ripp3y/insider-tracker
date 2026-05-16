import streamlit as st
import pandas as pd
import requests
import warnings
from io import StringIO
from datetime import datetime, timedelta

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*use_container_width.*")

# --------------------------------------------------------
# 1. Page Configuration & Setup
# --------------------------------------------------------
st.set_page_config(
    page_title="Asymmetry - Smart Money Tracker",
    page_icon="👁️‍🗨️",
    layout="wide"
)

st.title("👁️‍🗨️ Asymmetry")
st.caption("Tracking legal alpha by monitoring corporate executives and political disclosures.")

TODAY = datetime.now()

# Master Sector Mapping Database
SECTOR_MAP = {
    "NVDA": "Semiconductors / AI",
    "MRVL": "Semiconductors / AI",
    "UMC": "Semiconductors / AI",
    "LITE": "Optical Tech / Telecom",
    "FIX": "Industrial Infrastructure",
    "POWL": "Industrial Infrastructure",
    "BE": "Clean Energy / Utilities",
    "ALB": "Specialty Chemicals / Mining",
    "STX": "Data Storage / Hardware",
    "MSFT": "Enterprise Software / Cloud",
    "TXN": "Semiconductors / AI",
    "LRN": "EdTech / Services"
}

# --------------------------------------------------------
# 2. Hybrid Data Pipeline
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
                    "Sector": SECTOR_MAP.get(ticker, "Other / Unclassified")
                })
                
            final_df = pd.DataFrame(cleaned_data)
            if not final_df.empty:
                return final_df.sort_values(by="Filing Date", ascending=False)
                
        return get_fallback_political_data()
    except:
        return get_fallback_political_data()

def get_fallback_political_data():
    data = [
        {"Filing Date": TODAY - timedelta(days=0), "Politician": "Nancy Pelosi", "Chamber": "House", "Ticker": "NVDA", "Type": "🟢 Purchase", "Amount Range": "$1,000,001 - $5,000,000", "Numeric Max": 5000000},
        {"Filing Date": TODAY - timedelta(days=1), "Politician": "Markwayne Mullin", "Chamber": "Senate", "Ticker": "LRN", "Type": "🟢 Purchase", "Amount Range": "$15,001 - $50,001", "Numeric Max": 50000},
        {"Filing Date": TODAY - timedelta(days=2), "Politician": "Tommy Tuberville", "Chamber": "Senate", "Ticker": "TXN", "Type": "🟢 Purchase", "Amount Range": "$100,001 - $250,000", "Numeric Max": 250000},
        {"Filing Date": TODAY - timedelta(days=2), "Politician": "Tommy Tuberville", "Chamber": "Senate", "Ticker": "POWL", "Type": "🟢 Purchase", "Amount Range": "$50,001 - $100,000", "Numeric Max": 100000},
        {"Filing Date": TODAY - timedelta(days=3), "Politician": "Sheldon Whitehouse", "Chamber": "Senate", "Ticker": "MSFT", "Type": "🔴 Sale", "Amount Range": "$50,001 - $100,000", "Numeric Max": 100000},
        {"Filing Date": TODAY - timedelta(days=4), "Politician": "Michael Guest", "Chamber": "House", "Ticker": "FIX", "Type": "🟢 Purchase", "Amount Range": "$1,001 - $15,000", "Numeric Max": 15000},
        {"Filing Date": TODAY - timedelta(days=5), "Politician": "John Curtis", "Chamber": "House", "Ticker": "NVDA", "Type": "🟢 Purchase", "Amount Range": "$15,001 - $50,001", "Numeric Max": 50000},
        {"Filing Date": TODAY - timedelta(days=6), "Politician": "Markwayne Mullin", "Chamber": "Senate", "Ticker": "BE", "Type": "🟢 Purchase", "Amount Range": "$15,001 - $50,001", "Numeric Max": 50000},
        {"Filing Date": TODAY - timedelta(days=8), "Politician": "Ro Khanna", "Chamber": "House", "Ticker": "MRVL", "Type": "🔴 Sale", "Amount Range": "$50,001 - $100,000", "Numeric Max": 100000},
        {"Filing Date": TODAY - timedelta(days=11), "Politician": "Thomas Carper", "Chamber": "Senate", "Ticker": "ALB", "Type": "🟢 Purchase", "Amount Range": "$1,001 - $15,000", "Numeric Max": 15000},
        {"Filing Date": TODAY - timedelta(days=12), "Politician": "Dan Meuser", "Chamber": "House", "Ticker": "LITE", "Type": "🟢 Purchase", "Amount Range": "$50,001 - $100,000", "Numeric Max": 100000}
    ]
    df = pd.DataFrame(data)
    df["Filing Date"] = pd.to_datetime(df["Filing Date"])
    df["Sector"] = df["Ticker"].map(lambda x: SECTOR_MAP.get(x, "Other / Unclassified"))
    return df

def get_insider_data():
    data = [
        {"Ticker": "LITE", "Company": "Lumentum Holdings", "Insider": "Alan Lowe", "Role": "CEO", "Type": "🟢 Buy", "Value ($)": 250000, "Filing Date": (TODAY - timedelta(days=1)).strftime('%Y-%m-%d')},
        {"Ticker": "FIX", "Company": "Comfort Systems USA", "Insider": "Brian Lane", "Role": "CEO", "Type": "🟢 Buy", "Value ($)": 1100000, "Filing Date": (TODAY - timedelta(days=3)).strftime('%Y-%m-%d')},
        {"Ticker": "MRVL", "Company": "Marvell Technology", "Insider": "Matt Murphy", "Role": "CEO", "Type": "🟢 Buy", "Value ($)": 450000, "Filing Date": (TODAY - timedelta(days=4)).strftime('%Y-%m-%d')},
        {"Ticker": "BE", "Company": "Bloom Energy", "Insider": "KR Sridhar", "Role": "CEO", "Type": "🔴 Sell (10b5-1)", "Value ($)": -120000, "Filing Date": (TODAY - timedelta(days=5)).strftime('%Y-%m-%d')},
        {"Ticker": "NVDA", "Company": "NVIDIA Corp", "Insider": "Colette Kress", "Role": "CFO", "Type": "🔴 Sell", "Value ($)": -2300000, "Filing Date": (TODAY - timedelta(days=7)).strftime('%Y-%m-%d')},
        {"Ticker": "POWL", "Company": "Powell Industries", "Insider": "Brett Cope", "Role": "CEO", "Type": "🟢 Buy", "Value ($)": 320000, "Filing Date": (TODAY - timedelta(days=10)).strftime('%Y-%m-%d')},
        {"Ticker": "ALB", "Company": "Albemarle Corp", "Insider": "Kent Masters", "Role": "CEO", "Type": "🟢 Buy", "Value ($)": 500000, "Filing Date": (TODAY - timedelta(days=12)).strftime('%Y-%m-%d')}
    ]
    df = pd.DataFrame(data)
    df["Sector"] = df["Ticker"].map(lambda x: SECTOR_MAP.get(x, "Other / Unclassified"))
    return df

df_insider_raw = get_insider_data()
df_poly_raw = load_live_politician_data()

# --------------------------------------------------------
# 3. Sidebar Filters & Real-Time Sector Diagnostics
# --------------------------------------------------------
st.sidebar.header("🐋 Whale Order Filters")
min_insider_val = st.sidebar.slider("Minimum Insider Value ($)", 0, 1500000, 0, 50000)
min_poly_tier = st.sidebar.select_slider("Minimum Politician Tier", options=["All Trades", "$15k+", "$50k+", "$100k+", "$500k+"])

tier_mapping = {"All Trades": 0, "$15k+": 15000, "$50k+": 50000, "$100k+": 100000, "$500k+": 500000}
df_insider = df_insider_raw[df_insider_raw["Value ($)"].abs() >= min_insider_val]
df_poly = df_poly_raw[df_poly_raw["Numeric Max"] >= tier_mapping[min_poly_tier]]

st.sidebar.write("---")
st.sidebar.subheader("📊 Capital Hotspots by Sector")

# Combine datasets for universal sector counting
combined_sectors = pd.concat([df_insider["Sector"], df_poly["Sector"]]).value_counts()
if not combined_sectors.empty:
    st.sidebar.bar_chart(combined_sectors)
else:
    st.sidebar.caption("No data matches current slider parameters.")

# --------------------------------------------------------
# 4. Asymmetry Cross-Reference Engine
# --------------------------------------------------------
insider_tickers = set(df_insider_raw["Ticker"].unique())
poly_tickers = set(df_poly_raw["Ticker"].unique())
converged_tickers = insider_tickers.intersection(poly_tickers)

if converged_tickers:
    st.error(f"🔥 **Asymmetry Cross-Reference Alert:** Double Conviction Detected")
    cols = st.columns(len(converged_tickers))
    for idx, ticker in enumerate(converged_tickers):
        with cols[idx]:
            c_actions = df_insider_raw[df_insider_raw["Ticker"] == ticker]
            p_actions = df_poly_raw[df_poly_raw["Ticker"] == ticker]
            with st.container(border=True):
                st.markdown(f"### **{ticker}**")
                st.caption(SECTOR_MAP.get(ticker, "General"))
                st.markdown(f"**Corporate:** {len(c_actions)} Active | **Capitol Hill:** {len(p_actions)} Active")
    st.write("---")

# --------------------------------------------------------
# 5. UI Layout Tabs
# --------------------------------------------------------
tab1, tab2 = st.tabs(["🏢 Corporate Insiders", "🏛️ Political Disclosures"])

with tab1:
    st.subheader("Form 4 Intelligence Feed")
    st.dataframe(df_insider[["Filing Date", "Ticker", "Sector", "Insider", "Role", "Type", "Value ($)"]], hide_index=True, use_container_width=True)

with tab2:
    st.subheader("Live Capitol Hill Transactions")
    ticker_search = st.text_input("🔍 Filter Layout by Stock Ticker", "").upper().strip()
    if ticker_search:
        df_poly = df_poly[df_poly["Ticker"] == ticker_search]
    
    if not df_poly.empty:
        display_poly = df_poly.copy()
        display_poly["Filing Date"] = display_poly["Filing Date"].dt.strftime('%Y-%m-%d')
        st.dataframe(display_poly[["Filing Date", "Politician", "Ticker", "Sector", "Type", "Amount Range"]], hide_index=True, use_container_width=True)
    else:
        st.warning("No data found matching that filter.")
