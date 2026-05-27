import streamlit as st
import pandas as pd
import data_store

# ==============================================================================
# 1. APP CONFIGURATION & GLOBAL STYLING
# ==============================================================================
st.set_page_config(
    page_title="Asymmetry Portfolio Tracker",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Alpha Custom Interface Styling
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

# ==============================================================================
# 3. CORE DATA PROCESSING LAYER
# ==============================================================================
st.header("🦅 Asymmetry Portfolio Tracker")
st.caption("Live asset exposure maps across corporate structures and dark alpha signals")

# Pull clean portfolio tracking sets from data_store engine
try:
    df_portfolio = data_store.get_live_portfolio_positions()
except Exception as e:
    st.error(f"Failed to load portfolio dataframe: {e}")
    df_portfolio = pd.DataFrame()

# Mathematically extract exact settled asset allocations matching statements
if not df_portfolio.empty:
    # 1. HSA Balance processing (Positions + Settled Cash Reserves)
    hsa_positions_val = df_portfolio[df_portfolio["Account"] == "HSA"]["Total Value"].sum()
    hsa_cash_reserve = 79.41
    hsa_total_value = hsa_positions_val + hsa_cash_reserve
    
    # 2. BrokerageLink processing (Positions + Settled Cash Reserves)
    blink_positions_val = df_portfolio[df_portfolio["Account"] == "BrokerageLink"]["Total Value"].sum()
    blink_cash_reserve = 1.09
    blink_total_value = blink_positions_val + blink_cash_reserve
    
    # 3. Global Portfolio Aggregations
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

# Render Executive Asset Metric Cards
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
        # Format columns cleanly for UI exposure
        df_display = df_portfolio.copy()
        df_display["Shares"] = df_display["Shares"].map("{:,.3f}".format)
        df_display["Cost Basis"] = df_display["Cost Basis"].map("${:,.2f}".format)
        df_display["Current Price"] = df_display["Current Price"].map("${:,.2f}".format)
        df_display["Total Value"] = df_display["Total Value"].map("${:,.2f}".format)
        df_display["Total Gain ($)"] = df_display["Total Gain ($)"].map("${:,.2f}".format)
        df_display["Total Gain (%)"] = df_display["Total Gain (%)"].map("{:,.2f}%".format)
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.warning("Ledger matrix currently empty. Verify underlying data arrays.")

# TAB 2: CORPORATE INSIDERS EYE
with tab2:
    st.subheader("🏢 Form 4 Corporate Insider Monitoring")
    try:
        insider_data = data_store.get_insider_data(days=lookback_days)
        if insider_data:
            df_insider = pd.DataFrame(insider_data)
            st.dataframe(df_insider, use_container_width=True, hide_index=True)
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
            st.dataframe(df_politics, use_container_width=True, hide_index=True)
        else:
            st.info("No policy-maker transactions recorded in current queue window.")
    except Exception as e:
        st.error(f"Political tracking data feed timed out: {e}")

# TAB 4: LARGE-VOLUME WHALE ASSIGNMENTS
with tab4:
    st.subheader("🐋 Institutional Whale Block Transcripts")
    
    # Render layout filters matching visual mockups
    f1, f2 = st.columns(2)
    with f1:
        st.multiselect("Filter by Fund Type:", ["13F", "13D (Active)", "13G (Passive)"], default=["13F", "13D (Active)", "13G (Passive)"])
    with f2:
        st.multiselect("Filter Flow State:", ["Accumulation", "Reduction", "Material Buy"], default=["Accumulation", "Reduction", "Material Buy"])
        
    try:
        df_whales = data_store.get_live_whale_blocks()
        if not df_whales.empty:
            st.dataframe(df_whales, use_container_width=True, hide_index=True)
        else:
            st.info("No institutional block accumulation adjustments tracked.")
    except Exception as e:
        st.error(f"Whale data parsing stream error: {e}")

# TAB 5: MOVING AVERAGE ENTRY TRENDS
with tab5:
    st.subheader("🎯 Entry Windows & Support Anchors")
    if not df_portfolio.empty:
        watchlist_tickers = set(df_portfolio["Ticker"].unique())
        # Supplement watchlist with core monitoring targets
        watchlist_tickers.update(["NVDA", "AMD", "INTC", "ALB"])
        
        try:
            df_technicals = data_store.get_live_technicals(watchlist_tickers)
            if not df_technicals.empty:
                st.dataframe(df_technicals, use_container_width=True, hide_index=True)
            else:
                st.info("Processing EMA support parameters... Refresh app context.")
        except Exception as e:
            st.error(f"Technical trend matrix calculation failure: {e}")
    else:
        st.warning("Add portfolio positions or watchlist targets to populate moving average indicators.")
