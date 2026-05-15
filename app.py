import streamlit as st
import pandas as pd

# --------------------------------------------------------
# 1. Page Configuration & UI Accents
# --------------------------------------------------------
st.set_page_config(
    page_title="Asymmetry - Smart Money Tracker",
    page_icon="👁️‍🗨️",
    layout="wide"
)

# Native HTML injection to give the UI a clean dashboard feel
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

# --------------------------------------------------------
# 2. Expanded Data Processing Engines
# --------------------------------------------------------
def get_insider_data():
    # Expanded real-world tracking simulation across core sectors
    data = [
        {"Ticker": "LITE", "Company": "Lumentum Holdings", "Insider": "Alan Lowe", "Role": "CEO", "Type": "Buy", "Value ($)": 250000, "Position Change": "+45%", "Filing Date": "2026-05-14"},
        {"Ticker": "FIX", "Company": "Comfort Systems USA", "Insider": "Brian Lane", "Role": "CEO", "Type": "Buy", "Value ($)": 1100000, "Position Change": "+12%", "Filing Date": "2026-05-12"},
        {"Ticker": "MRVL", "Company": "Marvell Technology", "Insider": "Matt Murphy", "Role": "CEO", "Type": "Buy", "Value ($)": 450000, "Position Change": "+8%", "Filing Date": "2026-05-11"},
        {"Ticker": "BE", "Company": "Bloom Energy", "Insider": "KR Sridhar", "Role": "CEO", "Type": "Sell (10b5-1)", "Value ($)": -120000, "Position Change": "-1%", "Filing Date": "2026-05-10"},
        {"Ticker": "NVDA", "Company": "NVIDIA Corp", "Insider": "Colette Kress", "Role": "CFO", "Type": "Sell", "Value ($)": -2300000, "Position Change": "-4%", "Filing Date": "2026-05-08"},
        {"Ticker": "UMC", "Company": "United Microelectronics", "Insider": "Chien-Shan Chuan", "Role": "Director", "Type": "Buy", "Value ($)": 185000, "Position Change": "+15%", "Filing Date": "2026-05-07"},
        {"Ticker": "MSFT", "Company": "Microsoft Corp", "Insider": "Satya Nadella", "Role": "CEO", "Type": "Sell (10b5-1)", "Value ($)": -5400000, "Position Change": "-2%", "Filing Date": "2026-05-05"},
        {"Ticker": "POWL", "Company": "Powell Industries", "Insider": "Brett Cope", "Role": "CEO", "Type": "Buy", "Value ($)": 320000, "Position Change": "+22%", "Filing Date": "2026-05-04"},
        {"Ticker": "ALB", "Company": "Albemarle Corp", "Insider": "Kent Masters", "Role": "CEO", "Type": "Buy", "Value ($)": 620000, "Position Change": "+18%", "Filing Date": "2026-05-01"},
        {"Ticker": "STX", "Company": "Seagate Technology", "Insider": "Gianluca Romano", "Role": "CFO", "Type": "Buy", "Value ($)": 410000, "Position Change": "+11%", "Filing Date": "2026-04-28"},
        {"Ticker": "LASR", "Company": "nLIGHT Inc", "Insider": "Scott Keeney", "Role": "CEO", "Type": "Buy", "Value ($)": 95000, "Position Change": "+30%", "Filing Date": "2026-04-25"}
    ]
    return pd.DataFrame(data)

def get_politician_data():
    # Expanded legislative transaction list covering House & Senate filings
    data = [
        {"Politician": "Markwayne Mullin", "Chamber": "Senate (OK)", "Ticker": "LRN", "Asset": "Stride Inc", "Type": "Purchase", "Amount Range": "$15,001 - $50,000", "Filing Date": "2026-05-13"},
        {"Politician": "Nancy Pelosi", "Chamber": "House (CA)", "Ticker": "NVDA", "Asset": "NVIDIA Corp", "Type": "Purchase (Options)", "Amount Range": "$1,000,001 - $5,000,000", "Filing Date": "2026-05-10"},
        {"Politician": "Tommy Tuberville", "Chamber": "Senate (AL)", "Ticker": "TXN", "Asset": "Texas Instruments", "Type": "Purchase", "Amount Range": "$50,001 - $100,000", "Filing Date": "2026-05-09"},
        {"Politician": "John Michael Do", "Chamber": "House (TX)", "Ticker": "AAPL", "Asset": "Apple Inc", "Type": "Sale", "Amount Range": "$100,001 - $250,000", "Filing Date": "2026-05-05"},
        {"Politician": "Sheldon Whitehouse", "Chamber": "Senate (RI)", "Ticker": "MSFT", "Asset": "Microsoft Corp", "Type": "Purchase", "Amount Range": "$15,001 - $50,000", "Filing Date": "2026-05-02"},
        {"Politician": "Ro Khanna", "Chamber": "House (CA)", "Ticker": "MRVL", "Asset": "Marvell Technology", "Type": "Purchase", "Amount Range": "$50,001 - $100,000", "Filing Date": "2026-04-29"},
        {"Politician": "John Cornyn", "Chamber": "Senate (TX)", "Ticker": "COP", "Asset": "ConocoPhillips", "Type": "Sale", "Amount Range": "$15,001 - $50,000", "Filing Date": "2026-04-26"},
        {"Politician": "Dan Crenshaw", "Chamber": "House (TX)", "Ticker": "AMZN", "Asset": "Amazon.com Inc", "Type": "Purchase", "Amount Range": "$1,001 - $15,000", "Filing Date": "2026-04-22"}
    ]
    return pd.DataFrame(data)

# --------------------------------------------------------
# 3. Interactive Multi-Tab Interface
# --------------------------------------------------------
tab1, tab2 = st.tabs(["🏢 Corporate Insiders", "🏛️ Political Disclosures"])

# --- TAB 1: CORPORATE INSIDERS ---
with tab1:
    st.subheader("Form 4 Intelligence Feed")
    st.caption("Filtering out noise to focus on open-market insider sentiment.")
    
    df_insider = get_insider_data()
    
    # Active toggle to isolate out-of-pocket buyers
    filter_buys = st.checkbox("Show Open-Market Buys Only", value=False)
    if filter_buys:
        df_insider = df_insider[df_insider["Type"] == "Buy"]
        
    st.dataframe(
        df_insider,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Value ($)": st.column_config.NumberColumn(format="$%d")
        }
    )

# --- TAB 2: POLITICIANS ---
with tab2:
    st.subheader("Capitol Hill Trading Activity")
    st.caption("Tracking transaction disclosures filed by members of the U.S. House and Senate.")
    
    df_poly = get_politician_data()
    
    # Interactive filters for legislative branch tracking
    chamber_filter = st.multiselect("Filter by Chamber", ["Senate", "House"], default=["Senate", "House"])
    
    # Filter calculation logic
    mask = df_poly["Chamber"].str.contains("|".join(chamber_filter))
    df_poly_filtered = df_poly[mask]
    
    st.dataframe(
        df_poly_filtered,
        use_container_width=True,
        hide_index=True
    )
