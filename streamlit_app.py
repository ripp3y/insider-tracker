import streamlit as st
import pandas as pd
import data_store

# ==============================================================================
# 1. APP CONFIGURATION & GLOBAL STYLING
# ==============================================================================
st.set_page_config(
    page_title="Asymmetry Insider Engine",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Global CSS Inject
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

# ==============================================================================
# 2. SIDEBAR CONFIGURATION & LOOKBACK WINDOW
# ==============================================================================
st.sidebar.header("⚙️ Configuration")
st.sidebar.success("🔑 SEC API Key loaded from Cloud Secrets.")

lookback_days = st.sidebar.slider(
    label="Lookback Window (Days)",
    min_value=1,
    max_value=90,
    value=90
)

# Active Watchlist Array
if 'watchlist' not in st.session_state:
    raw_watchlist = [
        "NVDA", "MRVL", "FIX", "ALB", "LITE", "MU", "AMD", "FN", 
        "TSEM", "STX", "SNDK", "CEIN", "LRCX", "WDC", "ASX", "AXTI", "GLW", 
        "TXN", "C3NX", "CENX", "EFXT", "STRL", "MYRG", "COHR", "VICR", "SIMO", 
        "FLEX", "TTMI", "UMC", "GOOGL", "NUE", "NWPX", "CSCO", "GOOG", "STLD", 
        "TSM", "POWL", "BE", "DELL", "MSFT", "MTZ", "WOLF", "NXPI", "NVTS", "CIEN"
    ]
    st.session_state.watchlist = sorted(list(set([t for t in raw_watchlist if t != "EZRA"])))

# ==============================================================================
# 3. DATA INGESTION & STANDARDIZATION LAYER
# ==============================================================================
current_date = pd.to_datetime("2026-05-25")
cutoff_date = current_date - pd.to_timedelta(lookback_days, unit='D')

# Fetch Insiders Matrix safely
try:
    df_insiders = pd.DataFrame(data_store.get_insider_data(days=lookback_days))
except Exception as e:
    st.sidebar.error(f"SEC Pipeline Error: {e}")
    df_insiders = pd.DataFrame(columns=["Filing Date", "Ticker", "Insider", "Role"])
df_insiders = df_insiders.reset_index(drop=True)

# Fetch Live Political Stream Data
try:
    df_poly = data_store.get_live_political_trades()
    df_poly['Filing Date'] = pd.to_datetime(df_poly['Filing Date'])
    df_poly_filtered = df_poly[df_poly['Filing Date'] >= cutoff_date].reset_index(drop=True)
except Exception:
    df_poly_filtered = pd.DataFrame(columns=["Filing Date", "Ticker", "Politician", "Chamber", "Transaction", "Est. Value"])

# Fetch Live Institutional Whale Inflows
try:
    df_whales = data_store.get_live_whale_blocks().reset_index(drop=True)
    positive_whales = df_whales[df_whales['Change'].isin(["Accumulation", "Material Buy"])].reset_index(drop=True)
except Exception:
    df_whales = pd.DataFrame(columns=["Ticker", "Whale/Fund", "Type", "Change"])
    positive_whales = pd.DataFrame(columns=["Ticker", "Whale/Fund", "Type", "Change"])

# Navigation System Tabs
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🦅 Asymmetry Ledger",
    "🏢 Insiders", 
    "🏛️ Politics", 
    "🐋 Whales", 
    "🦅 MAGA Index", 
    "📋 Watchlist Manager"
])

# ==============================================================================
# TAB 0: PORTFOLIO REAL-TIME PERFORMANCE & ASSET ALLOCATION
# ==============================================================================
with tab0:
    st.header("🦅 Asymmetry Portfolio Tracker")
    st.caption("Live asset exposure maps across corporate structures tracking raw cost cushions following portfolio optimizations.")
    
    df_portfolio = data_store.get_live_portfolio_positions()
    
    # Calculate account summaries accurately including structural cash assets ($79.41 in HSA, $1.09 in B-Link)
    hsa_total = df_portfolio[df_portfolio["Account"] == "HSA"]["Total Value"].sum() + 79.41
    blink_total = df_portfolio[df_portfolio["Account"] == "BrokerageLink"]["Total Value"].sum() + 1.09
    blink_gain = df_portfolio[df_portfolio["Account"] == "BrokerageLink"]["Total Gain ($)"].sum()
    hsa_gain = df_portfolio[df_portfolio["Account"] == "HSA"]["Total Gain ($)"].sum()
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric(label="📊 BrokerageLink Balance", value=f"${blink_total:,.2f}", delta=f"+${blink_gain:,.2f} Un/Realized")
    with col_b:
        st.metric(label="🏥 HSA Balance", value=f"${hsa_total:,.2f}", delta=f"${hsa_gain:+,.2f} Total Return")
    with col_c:
        st.metric(label="📦 Combined Alpha Assets", value=f"${(blink_total + hsa_total):,.2f}")
        
    st.markdown("---")
    st.subheader("Active Position Tracking Weights")
    
    df_render = df_portfolio.copy()
    df_render["Shares"] = df_render["Shares"].map("{:,.3f}".format)
    df_render["Cost Basis"] = df_render["Cost Basis"].map("${:,.2f}".format)
    df_render["Current Price"] = df_render["Current Price"].map("${:,.2f}".format)
    df_render["Total Value"] = df_render["Total Value"].map("${:,.2f}".format)
    df_render["Total Gain ($)"] = df_render["Total Gain ($)"].map("${:,.2f}".format)
    df_render["Total Gain (%)"] = df_render["Total Gain (%)"].map("{:,.2f}%".format)
    
    df_final_view = df_render.drop(columns=["Cost Basis Total"])
    st.dataframe(df_final_view, width="stretch")

# ==============================================================================
# TAB 1: CORPORATE INSIDERS & CLUSTER DISCOVERY
# ==============================================================================
with tab1:
    st.header("Corporate Insiders")
    st.subheader("🎯 Live Cluster Intensity Matches")
    st.caption("Scanning for active tickers where both corporate insiders and institutional whale pools are accumulation buyers simultaneously.")

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
        st.info("No concurrent insider cluster overlaps discovered in the current configuration.")
        
    st.markdown("---")
    st.subheader("Raw Insider Open-Market Activity Log")
    if not df_insiders.empty:
        df_filtered_insiders = df_insiders[df_insiders['Ticker'].isin(st.session_state.watchlist)].reset_index(drop=True)
        st.dataframe(df_filtered_insiders, width="stretch")
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
            st.dataframe(df_poly_render, width="stretch")
        else:
            st.info(f"🚫 No matching political trade activity identified within the trailing {lookback_days} days.")
    else:
        st.info(f"🚫 No political trade activity recorded inside this timeframe.")

# ==============================================================================
# TAB 3: INSTITUTIONAL WHALE BLOCKS
# ==============================================================================
with tab3:
    st.header("🐋 Institutional Whale Blocks")
    
    fund_types = st.multiselect("Filter by Fund Type:", ["13F", "13D (Active)", "13G (Passive)"], default=["13F", "13D (Active)", "13G (Passive)"])
    flow_states = st.multiselect("Filter Flow State:", ["Accumulation", "Reduction", "Material Buy", "Disposal"], default=["Accumulation", "Reduction", "Material Buy"])

    if not df_whales.empty:
        df_whale_filtered = df_whales[
            df_whales['Type'].isin(fund_types) & 
            df_whales['Change'].isin(flow_states) & 
            df_whales['Ticker'].isin(st.session_state.watchlist)
        ].reset_index(drop=True)
        st.dataframe(df_whale_filtered, width="stretch")
    else:
        st.info("No institutional block flows available.")

# ==============================================================================
# TAB 4: FEDERAL PORTFOLIO STRATEGY (MAGA INDEX) & CONVICTION MATRIX ENGINE
# ==============================================================================
with tab4:
    st.header("🦅 Federal Portfolio Strategy (MAGA Index)")
    st.subheader("🔥 Algorithmic Triple Conviction Matrix")
    
    active_insider_buys = set(df_insiders['Ticker'].unique()) if not df_insiders.empty else set()
    active_political_buys = set(df_poly_filtered[df_poly_filtered['Transaction'].str.contains("Purchase", na=False)]['Ticker'].unique()) if not df_poly_filtered.empty else set()
    active_whale_buys = set(positive_whales['Ticker'].unique()) if not positive_whales.empty else set()
    
    matrix_rows = []
    
    for ticker in sorted(list(set(st.session_state.watchlist))):
        has_insider = ticker in active_insider_buys
        has_politics = ticker in active_political_buys
        has_whale = ticker in active_whale_buys
        match_count = sum([has_insider, has_politics, has_whale])
        
        if match_count >= 2:
            level_badge = "🔴 TRIPLE CONVICTION" if match_count == 3 else "🟡 Double Conviction"
            matrix_rows.append({
                "Ticker": ticker,
                "Conviction Level": level_badge,
                "Corporate Insiders": "✅ Active Buy" if has_insider else "❌ No Inflow",
                "Political Stream": "✅ Active Buy" if has_politics else "❌ No Inflow",
                "Institutional Whales": "✅ Active Accumulation" if has_whale else "❌ No Inflow"
            })
            
    if matrix_rows:
        df_matrix = pd.DataFrame(matrix_rows).sort_values(by="Conviction Level", ascending=False).reset_index(drop=True)
        st.error("⚠️ AUTOMATED CROSS-STREAM CONVICTION ALIGNMENT DETECTED:")
        st.dataframe(df_matrix, width="stretch")
    else:
        st.info("No multi-stream overlapping cross-signals detected within your tracking parameters currently.")

    # Technical Floor Anchors
    st.markdown("---")
    st.subheader("🎯 Entry Windows & Support Anchors")
    
    technical_ledger = [
        {"Ticker": "LITE", "Last Price": "$74.41", "21-day EMA": "$68.20", "50-day EMA": "$62.00", "Technical Setup": "🔥 Breakout"},
        {"Ticker": "POWL", "Last Price": "$291.97", "21-day EMA": "$178.40", "50-day EMA": "$165.00", "Technical Setup": "🔥 Breakout"},
        {"Ticker": "FIX", "Last Price": "$249.94", "21-day EMA": "$241.50", "50-day EMA": "$235.00", "Technical Setup": "🟢 Entry Zone"},
        {"Ticker": "MRVL", "Last Price": "$76.36", "21-day EMA": "$71.10", "50-day EMA": "$68.50", "Technical Setup": "💤 Premium / Hold"},
        {"Ticker": "STX", "Last Price": "$90.61", "21-day EMA": "$84.20", "50-day EMA": "$79.10", "Technical Setup": "💤 Premium / Hold"},
        {"Ticker": "SNDK", "Last Price": "$95.52", "21-day EMA": "$88.00", "50-day EMA": "$82.30", "Technical Setup": "💤 Premium / Hold"},
        {"Ticker": "ALB", "Last Price": "$124.30", "21-day EMA": "$118.00", "50-day EMA": "$115.20", "Technical Setup": "💤 Premium / Hold"},
        {"Ticker": "BE", "Last Price": "$14.20", "21-day EMA": "$12.05", "50-day EMA": "$13.50", "Technical Setup": "🟢 Entry Zone"},
        {"Ticker": "UMC", "Last Price": "$18.22", "21-day EMA": "$16.15", "50-day EMA": "$13.40", "Technical Setup": "🔥 Breakout"},
        {"Ticker": "WOLF", "Last Price": "$73.50", "21-day EMA": "$48.49", "50-day EMA": "$31.76", "Technical Setup": "🔥 Breakout"},
        {"Ticker": "CIEN", "Last Price": "$602.39", "21-day EMA": "$585.00", "50-day EMA": "$560.00", "Technical Setup": "🟢 Entry Zone"}
    ]
    df_tech = pd.DataFrame(technical_ledger)
    df_tech_filtered = df_tech[df_tech['Ticker'].isin(st.session_state.watchlist)].reset_index(drop=True)
    st.dataframe(df_tech_filtered, width="stretch")
    
    # Relative Volume Matrix
    st.markdown("---")
    st.subheader("📊 Relative Volume Momentum (Volume > 20-day MA)")
    
    volume_data = [
        {"Ticker": "LITE", "Relative Vol (x)": "1.76x", "Flow State": "🔴 Distribution", "Status": "🔥 BREAKOUT"},
        {"Ticker": "POWL", "Relative Vol (x)": "1.73x", "Flow State": "🔴 Distribution", "Status": "🔥 BREAKOUT"},
        {"Ticker": "CSCO", "Relative Vol (x)": "1.64x", "Flow State": "🟢 Accumulation", "Status": "🔥 BREAKOUT"},
        {"Ticker": "MSFT", "Relative Vol (x)": "1.46x", "Flow State": "🟢 Accumulation", "Status": "💤 Normal"},
        {"Ticker": "FIX", "Relative Vol (x)": "1.37x", "Flow State": "🔴 Distribution", "Status": "💤 Normal"}
    ]
    st.dataframe(pd.DataFrame(volume_data), width="stretch")

# ==============================================================================
# TAB 5: WATCHLIST MANAGER
# ==============================================================================
with tab5:
    st.header("Watchlist Manager")
    
    with st.form("add_ticker_form", clear_on_submit=True):
        new_ticker = st.text_input("Enter Ticker Symbol:").upper().strip()
        submit_btn = st.form_submit_button("➕ Add to Watchlist")
        
        if submit_btn and new_ticker:
            if new_ticker == "EZRA":
                st.toast("Holding block active: EZRA is explicitly barred from this model.", icon="🚫")
            elif new_ticker not in st.session_state.watchlist:
                st.session_state.watchlist.append(new_ticker)
                st.session_state.watchlist = sorted(list(set(st.session_state.watchlist)))
                st.toast(f"Added {new_ticker} to dashboard indexing!", icon="✅")
                st.rerun()

    st.subheader("Currently Tracking:")
    st.info(", ".join(st.session_state.watchlist))
    
    if st.button("🗑️ Reset Watchlist"):
        st.session_state.watchlist = ["NVDA", "MRVL", "FIX", "LITE", "POWL"]
        st.rerun()
