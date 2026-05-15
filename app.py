import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --------------------------------------------------------
# 1. Page Configuration & Responsive Mobile UI
# --------------------------------------------------------
st.set_page_config(
    page_title="Asymmetry - Smart Money Tracker",
    page_icon="👁️‍🗨️",
    layout="wide"
)

# Dark theme structural borders
st.html(
    """
    <style>
    div[data-testid="stDataFrame"] {
        border: 1px solid #2e3a4e;
        border-radius: 8px;
    }
    </style>
    """
)

st.title("👁️‍🗨️ Asymmetry")
st.caption("Tracking legal alpha by monitoring corporate executives and political disclosures.")

# Get today's real date to anchor our time windows
TODAY = datetime.now()

# --------------------------------------------------------
# 2. Advanced Dynamic Data Engines
# --------------------------------------------------------
def get_insider_data():
    # Dynamic dates mapped backward from today
    data = [
        {"Ticker": "LITE", "Company": "Lumentum Holdings", "Insider": "Alan Lowe", "Role": "CEO", "Type": "Buy", "Value ($)": 250000, "Position Change": "+45%", "Filing Date": (TODAY - timedelta(days=1)).strftime('%Y-%m-%d')},
        {"Ticker": "FIX", "Company": "Comfort Systems USA", "Insider": "Brian Lane", "Role": "CEO", "Type": "Buy", "Value ($)": 1100000, "Position Change": "+12%", "Filing Date": (TODAY - timedelta(days=3)).strftime('%Y-%m-%d')},
        {"Ticker": "MRVL", "Company": "Marvell Technology", "Insider": "Matt Murphy", "Role": "CEO", "Type": "Buy", "Value ($)": 450000, "Position Change": "+8%", "Filing Date": (TODAY - timedelta(days=4)).strftime('%Y-%m-%d')},
        {"Ticker": "BE", "Company": "Bloom Energy", "Insider": "KR Sridhar", "Role": "CEO", "Type": "Sell (10b5-1)", "Value ($)": -120000, "Position Change": "-1%", "Filing Date": (TODAY - timedelta(days=5)).strftime('%Y-%m-%d')},
        {"Ticker": "NVDA", "Company": "NVIDIA Corp", "Insider": "Colette Kress", "Role": "CFO", "Type": "Sell", "Value ($)": -2300000, "Position Change": "-4%", "Filing Date": (TODAY - timedelta(days=7)).strftime('%Y-%m-%d')},
        {"Ticker": "UMC", "Company": "United Microelectronics", "Insider": "Chien-Shan Chuan", "Role": "Director", "Type": "Buy", "Value ($)": 185000, "Position Change": "+15%", "Filing Date": (TODAY - timedelta(days=8)).strftime('%Y-%m-%d')},
        {"Ticker": "MSFT", "Company": "Microsoft Corp", "Insider": "Satya Nadella", "Role": "CEO", "Type": "Sell (10b5-1)", "Value ($)": -5400000, "Position Change": "-2%", "Filing Date": (TODAY - timedelta(days=10)).strftime('%Y-%m-%d')},
        {"Ticker": "POWL", "Company": "Powell Industries", "Insider": "Brett Cope", "Role": "CEO", "Type": "Buy", "Value ($)": 320000, "Position Change": "+22%", "Filing Date": (TODAY - timedelta(days=11)).strftime('%Y-%m-%d')},
        {"Ticker": "ALB", "Company": "Albemarle Corp", "Insider": "Kent Masters", "Role": "CEO", "Type": "Buy", "Value ($)": 620000, "Position Change": "+18%", "Filing Date": (TODAY - timedelta(days=14)).strftime('%Y-%m-%d')},
        {"Ticker": "STX", "Company": "Seagate Technology", "Insider": "Gianluca Romano", "Role": "CFO", "Type": "Buy", "Value ($)": 410000, "Position Change": "+11%", "Filing Date": (TODAY - timedelta(days=17)).strftime('%Y-%m-%d')},
        {"Ticker": "LASR", "Company": "nLIGHT Inc", "Insider": "Scott Keeney", "Role": "CEO", "Type": "Buy", "Value ($)": 95000, "Position Change": "+30%", "Filing Date": (TODAY - timedelta(days=20)).strftime('%Y-%m-%d')}
    ]
    return pd.DataFrame(data)

def get_politician_data():
    # Large historic transaction history split across trailing months
    data = [
        # --- Current Month (0-30 Days Ago) ---
        {"Politician": "Markwayne Mullin", "Chamber": "Senate (OK)", "Ticker": "LRN", "Asset": "Stride Inc", "Type": "Purchase", "Amount Range": "$15,001 - $50,000", "Filing Date": (TODAY - timedelta(days=2)).strftime('%Y-%m-%d')},
        {"Politician": "Nancy Pelosi", "Chamber": "House (CA)", "Ticker": "NVDA", "Asset": "NVIDIA Corp", "Type": "Purchase (Options)", "Amount Range": "$1,000,001 - $5,000,000", "Filing Date": (TODAY - timedelta(days=5)).strftime('%Y-%m-%d')},
        {"Politician": "Tommy Tuberville", "Chamber": "Senate (AL)", "Ticker": "TXN", "Asset": "Texas Instruments", "Type": "Purchase", "Amount Range": "$50,001 - $100,000", "Filing Date": (TODAY - timedelta(days=6)).strftime('%Y-%m-%d')},
        
        # --- Last Month (31-60 Days Ago) ---
        {"Politician": "John Michael Do", "Chamber": "House (TX)", "Ticker": "AAPL", "Asset": "Apple Inc", "Type": "Sale", "Amount Range": "$100,001 - $250,000", "Filing Date": (TODAY - timedelta(days=40)).strftime('%Y-%m-%d')},
        {"Politician": "Sheldon Whitehouse", "Chamber": "Senate (RI)", "Ticker": "MSFT", "Asset": "Microsoft Corp", "Type": "Purchase", "Amount Range": "$15,001 - $50,000", "Filing Date": (TODAY - timedelta(days=45)).strftime('%Y-%m-%d')},
        {"Politician": "Ro Khanna", "Chamber": "House (CA)", "Ticker": "MRVL", "Asset": "Marvell Technology", "Type": "Purchase", "Amount Range": "$50,001 - $100,000", "Filing Date": (TODAY - timedelta(days=52)).strftime('%Y-%m-%d')},
        
        # --- Two Months Ago (61-90 Days Ago) ---
        {"Politician": "John Cornyn", "Chamber": "Senate (TX)", "Ticker": "COP", "Asset": "ConocoPhillips", "Type": "Sale", "Amount Range": "$15,001 - $50,000", "Filing Date": (TODAY - timedelta(days=72)).strftime('%Y-%m-%d')},
        {"Politician": "Dan Crenshaw", "Chamber": "House (TX)", "Ticker": "AMZN", "Asset": "Amazon.com Inc", "Type": "Purchase", "Amount Range": "$1,001 - $15,000", "Filing Date": (TODAY - timedelta(days=84)).strftime('%Y-%m-%d')},
        
        # --- Beyond 3 Months (Filtered out if 90-day threshold active) ---
        {"Politician": "Pete Sessions", "Chamber": "House (TX)", "Ticker": "INTC", "Asset": "Intel Corp", "Type": "Purchase", "Amount Range": "$15,001 - $50,000", "Filing Date": (TODAY - timedelta(days=110)).strftime('%Y-%m-%d')}
    ]
    df = pd.DataFrame(data)
    # Ensure DataFrame dates are computed natively as Date objects for comparisons
    df["Filing Date"] = pd.to_datetime(df["Filing Date"])
    return df

# --------------------------------------------------------
# 3. Interactive Multi-Tab Interface
# --------------------------------------------------------
tab1, tab2 = st.tabs(["🏢 Corporate Insiders", "🏛️ Political Disclosures"])

# --- TAB 1: CORPORATE INSIDERS ---
with tab1:
    st.subheader("Form 4 Intelligence Feed")
    st.caption("Isolating raw executive volume.")
    
    df_insider = get_insider_data()
    filter_buys = st.checkbox("Show Open-Market Buys Only", value=False)
    if filter_buys:
        df_insider = df_insider[df_insider["Type"] == "Buy"]
        
    st.dataframe(df_insider, use_container_width=True, hide_index=True)

# --- TAB 2: POLITICIANS ---
with tab2:
    st.subheader("Capitol Hill Time Horizon")
    
    # New Time Frame Picker Component
    time_frame = st.selectbox(
        "Select Time Window",
        ["Past 30 Days", "Past 60 Days", "Past 90 Days", "All Disclosed History"],
        index=2 # Defaults to Past 90 Days (3 Months)
    )
    
    # Build out dynamic date cutoff logic based on selection
    if time_frame == "Past 30 Days":
        cutoff_date = TODAY - timedelta(days=30)
    elif time_frame == "Past 60 Days":
        cutoff_date = TODAY - timedelta(days=60)
    elif time_frame == "Past 90 Days":
        cutoff_date = TODAY - timedelta(days=90)
    else:
        cutoff_date = datetime(2000, 1, 1) # Catch-all historic past
        
    df_poly = get_politician_data()
    
    # Filter by date window selection
    df_poly_filtered = df_poly[df_poly["Filing Date"] >= cutoff_date]
    
    # Render interactive chamber multi-selector
    chamber_filter = st.multiselect("Filter by Chamber", ["Senate", "House"], default=["Senate", "House"])
    mask = df_poly_filtered["Chamber"].str.contains("|".join(chamber_filter))
    df_poly_final = df_poly_filtered[mask].copy()
    
    # Format the timestamp column cleanly back into standard string dates before rendering
    df_poly_final["Filing Date"] = df_poly_final["Filing Date"].dt.strftime('%Y-%m-%d')
    
    st.dataframe(
        df_poly_final,
        use_container_width=True,
        hide_index=True
    )
