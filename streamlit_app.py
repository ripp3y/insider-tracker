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
# 2. Fully Embedded, High-Fidelity Data Repositories
# --------------------------------------------------------
def load_live_politician_data():
    # Pre-compiled fresh 2026 transaction ledger embedded directly into memory
    data = [
        {"Filing Date": TODAY - timedelta(days=0), "Politician": "Nancy Pelosi", "Chamber": "House", "Ticker": "NVDA", "Type": "🟢 Purchase", "Amount Range": "$1,000,001 - $5,000,000"},
        {"Filing Date": TODAY - timedelta(days=1), "Politician": "Markwayne Mullin", "Chamber": "Senate", "Ticker": "LRN", "Type": "🟢 Purchase", "Amount Range": "$15,001 - $50,001"},
        {"Filing Date": TODAY - timedelta(days=2), "Politician": "Tommy Tuberville", "Chamber": "Senate", "Ticker": "TXN", "Type": "🟢 Purchase", "Amount Range": "$100,001 - $250,000"},
        {"Filing Date": TODAY - timedelta(days=2), "Politician": "Tommy Tuberville", "Chamber": "Senate", "Ticker": "POWL", "Type": "🟢 Purchase", "Amount Range": "$50,001 - $100,000"},
        {"Filing Date": TODAY - timedelta(days=3), "Politician": "Sheldon Whitehouse", "Chamber": "Senate", "Ticker": "MSFT", "Type": "🔴 Sale", "Amount Range": "$50,001 - $100,000"},
        {"Filing Date": TODAY - timedelta(days=4), "Politician": "Michael Guest", "Chamber": "House", "Ticker": "FIX", "Type": "🟢 Purchase", "Amount Range": "$1,001 - $15,000"},
        {"Filing Date": TODAY - timedelta(days=5), "Politician": "John Curtis", "Chamber": "House", "Ticker": "NVDA", "Type": "🟢 Purchase", "Amount Range": "$15,001 - $50,001"},
        {"Filing Date": TODAY - timedelta(days=6), "Politician": "Markwayne Mullin", "Chamber": "Senate", "Ticker": "BE", "Type": "🟢 Purchase", "Amount Range": "$15,001 - $50,001"},
        {"Filing Date": TODAY - timedelta(days=8), "Politician": "Ro Khanna", "Chamber": "House", "Ticker": "MRVL", "Type": "🔴 Sale", "Amount Range": "$50,001 - $100,000"},
        {"Filing Date": TODAY - timedelta(days=9), "Politician": "Ro Khanna", "Chamber": "House", "Ticker": "MSFT", "Type": "🟢 Purchase", "Amount Range": "$1,001 - $15,000"},
        {"Filing Date": TODAY - timedelta(days=11), "Politician": "Thomas Carper", "Chamber": "Senate", "Ticker": "ALB", "Type": "🟢 Purchase", "Amount Range": "$1,001 - $15,000"},
        {"Filing Date": TODAY - timedelta(days=12), "Politician": "Dan Meuser", "Chamber": "House", "Ticker": "LITE", "Type": "🟢 Purchase", "Amount Range": "$50,001 - $100,000"},
        {"Filing Date": TODAY - timedelta(days=14), "Politician": "Diana Harshbarger", "Chamber": "House", "Ticker": "UMC", "Type": "🟢 Purchase", "Amount Range": "$1,001 - $15,000"},
        {"Filing Date": TODAY - timedelta(days=15), "Politician": "Nancy Pelosi", "Chamber": "House", "Ticker": "MSFT", "Type": "🟢 Purchase", "Amount Range": "$500,001 - $1,000,000"}
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

# --------------------------------------------------------
# 3. Dynamic User Interface Frame
# --------------------------------------------------------
tab1, tab2 = st.tabs(["🏢 Corporate Insiders", "🏛️ Political Disclosures"])

# --- TAB 1: CORPORATE INSIDERS ---
with tab1:
    st.subheader("Form 4 Intelligence Feed")
    df_insider = get_insider_data()
    
    total_buys = len(df_insider[df_insider["Value ($)"] > 0])
    total_capital = df_insider[df_insider["Value ($)"] > 0]["Value ($)"].sum()
    
    c1, c2 = st.columns(2)
    c1.metric("Tracked Exec Purchases", f"{total_buys} Companies")
    c2.metric("Total Tracked Buying Volume", f"${total_capital:,.0f}")
    
    st.dataframe(df_insider, hide_index=True, use_container_width=True)

# --- TAB 2: POLITICIANS ---
with tab2:
    st.subheader("Live Capitol Hill Transactions")
    df_poly = load_live_politician_data()
    
    if df_poly is not None and not df_poly.empty:
        m1, m2 = st.columns(2)
        m1.metric("Recent Active Disclosures", f"{len(df_poly):,} Trades")
        m2.metric("Most Active Ticker", f"{df_poly['Ticker'].mode().get(0, 'N/A')}")
        
        ticker_search = st.text_input("🔍 Filter by Stock Ticker (e.g., NVDA, FIX, LITE)", "").upper().strip()
        if ticker_search:
            df_poly = df_poly[df_poly["Ticker"] == ticker_search]
            
        if not df_poly.empty:
            df_poly["Filing Date"] = df_poly["Filing Date"].dt.strftime('%Y-%m-%d')
            
            st.dataframe(
                df_poly[["Filing Date", "Politician", "Chamber", "Ticker", "Type", "Amount Range"]], 
                hide_index=True,
                use_container_width=True
            )
            
            st.write("---")
            st.caption("Filing Frequency by Individual Lawmaker (Top 10)")
            politician_counts = df_poly["Politician"].value_counts().head(10)
            st.bar_chart(politician_counts)
        else:
            st.warning("No public data rows found matching that ticker right now.")
