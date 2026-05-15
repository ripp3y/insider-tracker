import streamlit as st
import pandas as pd

# --------------------------------------------------------
# 1. Page Configuration & Styling
# --------------------------------------------------------
st.set_page_config(
    page_title="Asymmetry - Smart Money Tracker",
    page_icon="👁️‍🗨️",
    layout="wide"
)

# Dark, ultra-clean styling accents
st.markdown("""
    <style>
    .metric-card {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #3b82f6;
    }
    .politician-card {
        border-left: 5px solid #ef4444;
    }
    </style>
""", unsafe_html=True)

st.title("👁️‍🗨️ Asymmetry")
st.caption("Tracking legal alpha by monitoring corporate executives and political disclosures.")

# --------------------------------------------------------
# 2. Mock Data Engines (Ready for Real REST API Swap)
# --------------------------------------------------------
def get_insider_data():
    # Fields replicate clean Form 4 metrics focusing on "Skin in the Game"
    data = [
        {"Ticker": "LITE", "Company": "Lumentum Holdings", "Insider": "Alan Lowe", "Role": "CEO", "Type": "Buy", "Value ($)": 250000, "Position Change": "+45%", "Filing Date": "2026-05-14"},
        {"Ticker": "FIX", "Company": "Comfort Systems USA", "Insider": "Brian Lane", "Role": "CEO", "Type": "Buy", "Value ($)": 1100000, "Position Change": "+12%", "Filing Date": "2026-05-12"},
        {"Ticker": "MRVL", "Company": "Marvell Technology", "Insider": "Matt Murphy", "Role": "CEO", "Type": "Buy", "Value ($)": 450000, "Position Change": "+8%", "Filing Date": "2026-05-11"},
        {"Ticker": "BE", "Company": "Bloom Energy", "Insider": "KR Sridhar", "Role": "CEO", "Type": "Sell (10b5-1)", "Value ($)": -120000, "Position Change": "-1%", "Filing Date": "2026-05-10"},
        {"Ticker": "NVDA", "Company": "NVIDIA Corp", "Insider": "Colette Kress", "Role": "CFO", "Type": "Sell", "Value ($)": -2300000, "Position Change": "-4%", "Filing Date": "2026-05-08"}
    ]
    return pd.DataFrame(data)

def get_politician_data():
    # Fields map directly to House/Senate PTR (Periodic Transaction Report) filings
    data = [
        {"Politician": "Markwayne Mullin", "Chamber": "Senate (OK)", "Ticker": "LRN", "Asset": "Stride Inc", "Type": "Purchase", "Amount Range": "$15,001 - $50,000", "Filing Date": "2026-05-13"},
        {"Politician": "Nancy Pelosi", "Chamber": "House (CA)", "Ticker": "NVDA", "Asset": "NVIDIA Corp", "Type": "Purchase (Options)", "Amount Range": "$1,000,001 - $5,000,000", "Filing Date": "2026-05-10"},
        {"Politician": "Tommy Tuberville", "Chamber": "Senate (AL)", "Ticker": "TXN", "Asset": "Texas Instruments", "Type": "Purchase", "Amount Range": "$50,001 - $100,000", "Filing Date": "2026-05-09"},
        {"Politician": "John Michael Do", "Chamber": "House (TX)", "Ticker": "AAPL", "Asset": "Apple Inc", "Type": "Sale", "Amount Range": "$100,001 - $250,000", "Filing Date": "2026-05-05"}
    ]
    return pd.DataFrame(data)

# --------------------------------------------------------
# 3. Main Interface Layout (The Two Tabs)
# --------------------------------------------------------
tab1, tab2 = st.tabs(["🏢 Corporate Insiders", "🏛️ Political Disclosures"])

# --- TAB 1: CORPORATE INSIDERS ---
with tab1:
    st.subheader("Form 4 Intelligence Feed")
    st.markdown("> *Tip: Look for Cluster Buying—where multiple executives load up on the same stock out-of-pocket.*")
    
    df_insider = get_insider_data()
    
    # Simple interactive filter to strip away routine automated sales if needed
    filter_buys = st.checkbox("Show Open-Market Buys Only", value=False)
    if filter_buys:
        df_insider = df_insider[df_insider["Type"] == "Buy"]
        
    st.dataframe(
        df_insider,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Value ($)": st.column_config.NumberColumn(format="$%d"),
            "Position Change": st.column_config.TextColumn()
        }
    )

# --- TAB 2: POLITICIANS ---
with tab2:
    st.subheader("Capitol Hill Trading Activity")
    st.markdown("> *Note: Federal law requires Congress members to report transactions within 45 days. This tracks high-volume policy-adjacent moves.*")
    
    df_poly = get_politician_data()
    
    # Filter by House or Senate
    chamber_filter = st.multiselect("Filter by Chamber", ["Senate", "House"], default=["Senate", "House"])
    
    # Simple regex parsing to match chamber selection
    mask = df_poly["Chamber"].str.contains("|".join(chamber_filter))
    df_poly_filtered = df_poly[mask]
    
    st.dataframe(
        df_poly_filtered,
        use_container_width=True,
        hide_index=True
    )

