import streamlit as st
import pandas as pd

# ==============================================================================
# 1. APP CONFIGURATION & SIDEBAR
# ==============================================================================
st.set_page_config(
    page_title="Asymmetry Insider Engine",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# FIXED: Removed the buggy 'unsafe_gradient' argument throwing the TypeError
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    .stAlert { margin-top: 1rem; }
    .metric-card {
        background-color: #1e2430;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #00ffcc;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.sidebar.header("⚙️ Configuration")
st.sidebar.success("🔑 SEC API Key loaded from Cloud Secrets.")

# Lookback Window Slider
lookback_days = st.sidebar.slider(
    label="Lookback Window (Days)",
    min_value=1,
    max_value=90,
    value=90
)

# Active Watchlist Array (Ensuring complete item uniqueness to avoid Pandas index collisions)
if 'watchlist' not in st.session_state:
    raw_watchlist = [
        "NVDA", "INTC", "MRVL", "FIX", "ALB", "LITE", "MU", "AMD", "FN", 
        "TSEM", "STX", "SNDK", "CEIN", "LRCX", "WDC", "ASX", "AXTI", "GLW", 
        "TXN", "C3NX", "CENX", "EFXT", "STRL", "MYRG", "COHR", "VICR", "SIMO", 
        "FLEX", "TTMI", "UMC", "GOOGL", "NUE", "NWPX", "CSCO", "GOOG", "STLD", 
        "TSM", "POWL", "BE", "DELL", "MSFT", "MTZ"
    ]
    # Filter out EZRA just in case it attempts to creep into active memory frames
    st.session_state.watchlist = sorted(list(set([t for t in raw_watchlist if t != "EZRA"])))

# ==============================================================================
# DATA INGESTION & STANDARDIZATION LAYER (LIVE API CONNECTED)
# ==============================================================================
import data_store

current_date = pd.to_datetime("2026-05-25")
cutoff_date = current_date - pd.to_timedelta(lookback_days, unit='D')

# 1. Fetch Dynamic Insiders Matrix safely
try:
    df_insiders = pd.DataFrame(data_store.get_insider_data(days=lookback_days))
except Exception as e:
    st.sidebar.error(f"SEC Pipeline Error: {e}")
    df_insiders = pd.DataFrame(columns=["Filing Date", "Ticker", "Insider", "Role"])
df_insiders = df_insiders.reset_index(drop=True)

# 2. Fetch Live Political Stream Data from API
try:
    df_poly = data_store.get_live_political_trades()
    df_poly['Filing Date'] = pd.to_datetime(df_poly['Filing Date'])
    df_poly_filtered = df_poly[df_poly['Filing Date'] >= cutoff_date].reset_index(drop=True)
except Exception:
    df_poly_filtered = pd.DataFrame(columns=["Filing Date", "Ticker", "Politician", "Chamber", "Transaction", "Est. Value"])

# 3. Fetch Live Institutional Whale Inflows
try:
    df_whales = data_store.get_live_whale_blocks().reset_index(drop=True)
    positive_whales = df_whales[df_whales['Change'].isin(["Accumulation", "Material Buy"])].reset_index(drop=True)
except Exception:
    df_whales = pd.DataFrame(columns=["Ticker", "Whale/Fund", "Type", "Change"])
    positive_whales = pd.DataFrame(columns=["Ticker", "Whale/Fund", "Type", "Change"])

# Navigation Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏢 Insiders", 
    "🏛️ Politics", 
    "🐋 Whales", 
    "🦅 MAGA Index", 
    "📋 Watchlist Manager"
])

# ==============================================================================
# TAB 1: CORPORATE INSIDERS & CLUSTER DISCOVERY
# ==============================================================================
with tab1:
    st.header("Corporate Insiders")
    st.subheader("🎯 Live Cluster Intensity Matches")
    st.caption("Automatically scanning for active tickers where both corporate insiders and 13F/D/G institutional whales are accumulation buyers simultaneously.")

    if not df_insiders.empty and not positive_whales.empty:
        insider_tickers = set(df_insiders['Ticker'].unique())
        whale_tickers = set(positive_whales['Ticker'].unique())
        cluster_targets = insider_tickers.intersection(whale_tickers).intersection(set(st.session_state.watchlist))
    else:
        cluster_targets = set()
    
    if cluster_targets:
        cols = st.columns(len(cluster_targets) if len(cluster_targets) <= 4 else 4)
        for idx, ticker in enumerate(sorted(cluster_targets)):
            col_target = cols[idx % 4]
            insider_count = len(df_insiders[df_insiders['Ticker'] == ticker])
            whale_count = len(positive_whales[positive_whales['Ticker'] == ticker])
            density_score = insider_count + whale_count
            
            with col_target:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style='margin:0; color:#00ffcc;'>🔥 {ticker}</h3>
                    <p style='margin:5px 0 0 0; font-size:14px; color:#b0c4de;'>
                        Cluster Density Score: <b>{density_score}</b><br>
                        • Insiders Actively Buying: <b>{insider_count}</b><br>
                        • Institutional Funds Buying: <b>{whale_count}</b>
                    </p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No concurrent insider cluster overlaps discovered in the current lookback window configuration.")
        
    st.markdown("---")
    st.subheader("Raw Insider Open-Market Activity Log")
    if not df_insiders.empty:
        df_filtered_insiders = df_insiders[df_insiders['Ticker'].isin(st.session_state.watchlist)].reset_index(drop=True)
        st.dataframe(df_filtered_insiders, use_container_width=True)
    else:
        st.info("Insider activity stream is currently empty.")

# ==============================================================================
# TAB 2: POLITICAL TRADES
# ==============================================================================
with tab2:
    st.header("Political Trades")
    
    if not df_poly_filtered.empty:
        df_poly_render = df_poly_filtered[df_poly_filtered['Ticker'].isin(st.session_state.watchlist)].sort_values(by="Filing Date", ascending=False).reset_index(drop=True)
        if not df_poly_render.empty:
            df_poly_render['Filing Date'] = df_poly_render['Filing Date'].dt.strftime('%Y-%m-%d')
            st.dataframe(df_poly_render, use_container_width=True)
        else:
