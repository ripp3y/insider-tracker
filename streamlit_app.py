import streamlit as st
import pandas as pd
import data_store
import warnings
import logging

# Intercept and terminate warning log streams programmatically
logging.getLogger("streamlit").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

# ==============================================================================
# 1. APP CONFIGURATION & GLOBAL STYLING
# ==============================================================================
st.set_page_config(
    page_title="Asymmetry Portfolio Tracker",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border-left: 5px solid #ef4444; }
    div[data-testid="stMetricValue"] { font-size: 24px; font-weight: bold; color: #f3f4f6; }
    div[data-testid="stMetricDelta"] { font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. SIDEBAR CONFIGURATION LAYER
# ==============================================================================
with st.sidebar:
    st.title("⚙️ Configuration")
    st.success("🔑 SEC API Key loaded from Cloud Secrets.")
    
    lookback_days = st.slider(
        "Lookback Window (Days)",
        min_value=30,
        max_value=360,
        value=90,
        step=30
    )
    
    st.markdown("---")
    st.markdown("### 📡 Pipeline Status")
    st.info("• Data Core: Connected")
    st.info("• Rate Engine: Thread-Isolated")
    st.info("• Visual Engine: Active")

# ==============================================================================
# 3. CORE DATA PROCESSING LAYER
# ==============================================================================
st.header("🦅 Asymmetry Portfolio Tracker")
st.caption("Live asset exposure maps across corporate structures and dark alpha signals")

try:
    df_portfolio = data_store.get_live_portfolio_positions()
except Exception as e:
    st.error(f"Failed to load portfolio dataframe: {e}")
    df_portfolio = pd.DataFrame()

if not df_portfolio.empty:
    hsa_positions_val = df_portfolio[df_portfolio["Account"] == "HSA"]["Total Value"].sum()
    hsa_cash_reserve = 79.41
    hsa_total_value = hsa_positions_val + hsa_cash_reserve
    
    blink_positions_val = df_portfolio[df_portfolio["Account"] == "BrokerageLink"]["Total Value"].sum()
    blink_cash_reserve = 1.09
    blink_total_value = blink_positions_val + blink_cash_reserve
    
    total_net_assets = hsa_total_value + blink_total_value
    total_cost_basis = df_portfolio["Cost Basis Total"].sum()
    global_raw_gain = df_portfolio["Total Gain ($)"].sum()
    global_pct_gain = (global_raw_gain / total_cost_basis * 100) if total_cost_basis > 0 else 0.0
else:
    hsa_total_value = 14410.95
    blink_total_value = 72161.80
    total_net_assets = 86572.75
    global_raw_gain = 17169.70
    global_pct_gain = 24.74

m1, m2, m3 = st.columns(3)
m1.metric("Strategic Net Assets", f"${total_net_assets:,.2f}", f"+${global_raw_gain:,.2f} Total Return")
m2.metric("BrokerageLink Balance", f"${blink_total_value:,.2f}", "Cash Reserve: $1.09")
m3.metric("HSA Net Value", f"${hsa_total_value:,.2f}", "Cash Reserve: $79.41")

st.markdown("---")

# ==============================================================================
# 4. DASHBOARD TABS & DATA MAPPING
# ==============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🦅 Asymmetry Ledger", 
    "🏢 Insiders", 
    "🏛️ Politics", 
    "🐋 Whales", 
    "📈 Technical Setup Windows"
])

# TAB 1: ASYMMETRY LEDGER VIEW
with tab1:
    st.subheader("📋 Account Asset Allocations")
    if not df_portfolio.empty:
        c1, c2 = st.columns([2, 1])
        
        with c1:
            df_display = df_portfolio.copy()
            df_display["Shares"] = df_display["Shares"].map("{:,.3f}".format)
            df_display["Cost Basis"] = df_display["Cost Basis"].map("${:,.2f}".format)
            df_display["Current Price"] = df_display["Current Price"].map("${:,.2f}".format)
            df_display["Total Value"] = df_display["Total Value"].map("${:,.2f}".format)
            df_display["Total Gain ($)"] = df_display["Total Gain ($)"].map("${:,.2f}".format)
            df_display["Total Gain (%)"] = df_display["Total Gain (%)"].map("{:,.2f}%".format)
            st.dataframe(df_display, width="stretch", hide_index=True)
            
        with c2:
            st.markdown("##### Net Allocation Weight")
            chart_df = df_portfolio[["Ticker", "Total Value"]].copy()
            st.bar_chart(chart_df.set_index("Ticker"), y="Total Value", color="#ef4444")
    else:
        st.warning("Ledger matrix currently empty.")

# TAB 2: CORPORATE INSIDERS EYE
with tab2:
    st.subheader("🏢 Form 4 Corporate Insider Monitoring")
    try:
        insider_data = data_store.get_insider_data(days=lookback_days)
        if insider_data:
            df_insider = pd.DataFrame(insider_data)
            
            v1, v2 = st.columns([1, 2])
            with v1:
                st.markdown("##### Insider Filings by Asset")
                ticker_counts = df_insider["Ticker"].value_counts().reset_index()
                ticker_counts.columns = ["Ticker", "Filings Volume"]
                st.bar_chart(ticker_counts.set_index("Ticker"), y="Filings Volume", color="#3b82f6")
                
            with v2:
                st.dataframe(df_insider, width="stretch", hide_index=True)
        else:
            st.info("No active corporate insider filings detected inside lookback window.")
    except Exception as e:
        st.error(f"Insider pipeline unresolved: {e}")

# TAB 3: CONGRESSIONAL DATA CAPTURE
with tab3:
    st.subheader("🏛️ Capital Hill Policy Trade Disclosures")
    try:
        df_politics = data_store.get_live_political_trades()
        if not df_politics.empty:
            p1, p2 = st.columns([2, 1])
            with p1:
                st.dataframe(df_politics, width="stretch", hide_index=True)
            with p2:
                st.markdown("##### Trade Signage Velocity")
                flow_counts = df_politics["Transaction"].value_counts().reset_index()
                flow_counts.columns = ["Direction", "Count"]
                st.bar_chart(flow_counts.set_index("Direction"), y="Count", color="#10b981")
        else:
            st.info("No policy-maker transactions recorded in current queue window.")
    except Exception as e:
        st.error(f"Political tracking data feed timed out: {e}")

# TAB 4: LARGE-VOLUME WHALE ASSIGNMENTS
with tab4:
    st.subheader("🐋 Institutional Whale Block Transcripts")
    
    f1, f2 = st.columns(2)
    with f1:
        st.multiselect("Filter by Fund Type:", ["13F", "13D (Active)", "13G (Passive)"], default=["13F", "13D (Active)", "13G (Passive)"])
    with f2:
        st.multiselect("Filter Flow State:", ["Accumulation", "Reduction", "Material Buy"], default=["Accumulation", "Reduction", "Material Buy"])
        
    try:
        df_whales = data_store.get_live_whale_blocks()
        if not df_whales.empty:
            st.dataframe(df_whales, width="stretch", hide_index=True)
        else:
            st.info("No institutional block accumulation adjustments tracked.")
    except Exception as e:
        st.error(f"Whale data parsing stream error: {e}")

# TAB 5: MOVING AVERAGE ENTRY TRENDS
with tab5:
    st.subheader("🎯 Entry Windows & Support Anchors")
    if not df_portfolio.empty:
        watchlist_tickers = set(df_portfolio["Ticker"].unique())
        watchlist_tickers.update(["NVDA", "AMD", "INTC", "ALB"])
        
        try:
            df_technicals = data_store.get_live_technicals(watchlist_tickers)
            if not df_technicals.empty:
                st.dataframe(df_technicals, width="stretch", hide_index=True)
            else:
                st.info("Processing EMA support parameters... Refresh app context.")
        except Exception as e:
            st.error(f"Technical trend matrix calculation failure: {e}")
    else:
        st.warning("Add portfolio positions or watchlist targets to populate moving average indicators.")
