import streamlit as st
import pandas as pd
import warnings
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

# --------------------------------------------------------
# 2. Embedded Data Repositories
# --------------------------------------------------------
def load_live_politician_data():
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
        {"Filing Date": TODAY - timedelta(days=9), "Politician": "Ro Khanna", "Chamber": "House", "Ticker": "MSFT", "Type": "🟢 Purchase", "Amount Range": "$1,001 - $15,000", "Numeric Max": 15000},
        {"Filing Date": TODAY - timedelta(days=11), "Politician": "Thomas Carper", "Chamber": "Senate", "Ticker": "ALB", "Type": "🟢 Purchase", "Amount Range": "$1,001 - $15,000", "Numeric Max": 15000},
        {"Filing Date": TODAY - timedelta(days=12), "Politician": "Dan Meuser", "Chamber": "House", "Ticker": "LITE", "Type": "🟢 Purchase", "Amount Range": "$50,001 - $100,000", "Numeric Max": 100000},
        {"Filing Date": TODAY - timedelta(days=14), "Politician": "Diana Harshbarger", "Chamber": "House", "Ticker": "UMC", "Type": "🟢 Purchase", "Amount Range": "$1,001 - $15,000", "Numeric Max": 15000},
        {"Filing Date": TODAY - timedelta(days=15), "Politician": "Nancy Pelosi", "Chamber": "House", "Ticker": "MSFT", "Type": "🟢 Purchase", "Amount Range": "$500,001 - $1,000,000", "Numeric Max": 1000000}
    ]
    df = pd.DataFrame(data)
    df["Filing Date"] = pd.to_datetime(df["Filing Date"])
    return df.sort_values(by="Filing Date", ascending=False)

def get_insider_data():
    data = [
        {"Ticker": "LITE", "Company": "Lumentum Holdings", "Insider": "Alan Lowe", "Role": "CEO", "Type": "🟢 Buy", "Value ($)": 250000, "Filing Date": (TODAY - timedelta(days=1)).strftime('%Y-%m-%d')},
        {"Ticker": "FIX", "Company": "Comfort Systems USA", "Insider": "Brian Lane", "Role": "CEO", "Type": "🟢 Buy", "Value ($)": 1100000, "Filing Date": (TODAY - timedelta(days=3)).strftime('%Y-%m-%d')},
        {"Ticker": "MRVL", "Company": "Marvell Technology", "Insider": "Matt Murphy", "Role": "CEO", "Type": "🟢 Buy", "Value ($)": 450000, "Filing Date": (TODAY - timedelta(days=4)).strftime('%Y-%m-%d')},
        {"Ticker": "BE", "Company": "Bloom Energy", "Insider": "KR Sridhar", "Role": "CEO", "Type": "🔴 Sell (10b5-1)", "Value ($)": -120000, "Filing Date": (TODAY - timedelta(days=5)).strftime('%Y-%m-%d')},
        {"Ticker": "NVDA", "Company": "NVIDIA Corp", "Insider": "Colette Kress", "Role": "CFO", "Type": "🔴 Sell", "Value ($)": -2300000, "Filing Date": (TODAY - timedelta(days=7)).strftime('%Y-%m-%d')},
        {"Ticker": "UMC", "Company": "United Microelectronics", "Insider": "Chien-Shan Chuan", "Role": "Director", "Type": "🟢 Buy", "Value ($)": 85000, "Filing Date": (TODAY - timedelta(days=8)).strftime('%Y-%m-%d')},
        {"Ticker": "POWL", "Company": "Powell Industries", "Insider": "Brett Cope", "Role": "CEO", "Type": "🟢 Buy", "Value ($)": 320000, "Filing Date": (TODAY - timedelta(days=10)).strftime('%Y-%m-%d')},
        {"Ticker": "ALB", "Company": "Albemarle Corp", "Insider": "Kent Masters", "Role": "CEO", "Type": "🟢 Buy", "Value ($)": 500000, "Filing Date": (TODAY - timedelta(days=12)).strftime('%Y-%m-%d')},
        {"Ticker": "STX", "Company": "Seagate Technology", "Insider": "Gianluca Romano", "Role": "CFO", "Type": "🟢 Buy", "Value ($)": 140000, "Filing Date": (TODAY - timedelta(days=14)).strftime('%Y-%m-%d')}
    ]
    return pd.DataFrame(data)

# Load base dataframes for background logic
df_insider_raw = get_insider_data()
df_poly_raw = load_live_politician_data()

# --------------------------------------------------------
# 3. Sidebar Control Panel (High-Whale Filters)
# --------------------------------------------------------
st.sidebar.header("🐋 Whale Order Filters")
st.sidebar.caption("Filter out the noise and track high-conviction institutional positions.")

# Filter 1: Min Corporate Value
min_insider_val = st.sidebar.slider(
    "Minimum Insider Buy Value ($)", 
    min_value=0, 
    max_value=1500000, 
    value=0, 
    step=50000
)

# Filter 2: Min Politician Tier
min_poly_tier = st.sidebar.select_slider(
    "Minimum Politician Trade Tier",
    options=["All Trades", "$15k+", "$50k+", "$100k+", "$500k+"],
    value="All Trades"
)

# Map human-readable slider values to underlying numeric data ceilings
tier_mapping = {"All Trades": 0, "$15k+": 15000, "$50k+": 50000, "$100k+": 100000, "$500k+": 500000}
target_poly_ceiling = tier_mapping[min_poly_tier]

# Apply Whale Filters to generate active display dataframes
df_insider = df_insider_raw[
    (df_insider_raw["Value ($)"].abs() >= min_insider_val)
]
df_poly = df_poly_raw[
    (df_poly_raw["Numeric Max"] >= target_poly_ceiling)
]

# --------------------------------------------------------
# 4. Cross-Reference Intel Engine (Asymmetry Scanner)
# --------------------------------------------------------
# Isolate distinct tickers where both factions have active positions
insider_tickers = set(df_insider_raw["Ticker"].unique())
poly_tickers = set(df_poly_raw["Ticker"].unique())
converged_tickers = insider_tickers.intersection(poly_tickers)

if converged_tickers:
    st.error(f"🔥 **Asymmetry Cross-Reference Alert:** Double Conviction Detected")
    
    # Create clean display layout for cross-referenced positions
    cols = st.columns(len(converged_tickers))
    for index, ticker in enumerate(converged_tickers):
        with cols[index]:
            # Pull corporate activities
            c_actions = df_insider_raw[df_insider_raw["Ticker"] == ticker]
            p_actions = df_poly_raw[df_poly_raw["Ticker"] == ticker]
            
            with st.container(border=True):
                st.markdown(f"### **{ticker}**")
                st.caption("Active Sync Found Across Factions")
                st.markdown(f"**Corporate:** {len(c_actions)} Insiders Active")
                st.markdown(f"**Capitol Hill:** {len(p_actions)} Politicians Active")
    st.write("---")

# --------------------------------------------------------
# 5. Main Content Layout Tab Rendering
# --------------------------------------------------------
tab1, tab2 = st.tabs(["🏢 Corporate Insiders", "🏛️ Political Disclosures"])

# --- TAB 1: CORPORATE INSIDERS ---
with tab1:
    st.subheader("Form 4 Intelligence Feed")
    
    total_buys = len(df_insider[df_insider["Value ($)"] > 0])
    total_capital = df_insider[df_insider["Value ($)"] > 0]["Value ($)"].sum()
    
    c1, c2 = st.columns(2)
    c1.metric("Tracked Exec Purchases", f"{total_buys} Companies")
    c2.metric("Total Tracked Buying Volume", f"${total_capital:,.0f}")
    
    st.dataframe(df_insider.drop(columns=[], errors='ignore'), hide_index=True, use_container_width=True)

# --- TAB 2: POLITICIANS ---
with tab2:
    st.subheader("Live Capitol Hill Transactions")
    
    if df_poly is not None and not df_poly.empty:
        m1, m2 = st.columns(2)
        m1.metric("Recent Active Disclosures", f"{len(df_poly):,} Trades")
        m2.metric("Most Active Ticker", f"{df_poly['Ticker'].mode().get(0, 'N/A')}")
        
        ticker_search = st.text_input("🔍 Filter Layout by Stock Ticker", "").upper().strip()
        if ticker_search:
            df_poly = df_poly[df_poly["Ticker"] == ticker_search]
            
        if not df_poly.empty:
            # Format output dates smoothly
            display_poly = df_poly.copy()
            display_poly["Filing Date"] = display_poly["Filing Date"].dt.strftime('%Y-%m-%d')
            
            st.dataframe(
                display_poly[["Filing Date", "Politician", "Chamber", "Ticker", "Type", "Amount Range"]], 
                hide_index=True,
                use_container_width=True
            )
            
            st.write("---")
            st.caption("Filing Frequency by Individual Lawmaker (Top 10)")
            politician_counts = display_poly["Politician"].value_counts().head(10)
            st.bar_chart(politician_counts)
        else:
            st.warning("No public data rows found matching that ticker right now.")
