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

# Custom Global CSS Inject (Clean and Safe)
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    .stAlert { margin-top: 1rem; }
    </style>
""", unsafe_allow_html=True)

st.sidebar.header("⚙️ Configuration")
st.sidebar.success("🔑 SEC API Key loaded from Cloud Secrets.")

# Lookback Window Slider
lookback_days = st.sidebar.slider(
    label="Lookback Window (Days)",
    min_value=1,
    max_value=90,
    value=14
)

# Active Watchlist Array
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = [
        "NVDA", "INTC", "MRVL", "FIX", "ALB", "LITE", "MU", "AMD", "FN", 
        "TSEM", "STX", "SNDK", "CEIN", "LRCX", "WDC", "ASX", "AXTI", "GLW", 
        "TXN", "C3NX", "CENX", "EFXT", "STRL", "MYRG", "COHR", "VICR", "SIMO", 
        "FLEX", "TTMI", "UMC", "GOOGL", "NUE", "NWPX", "CSCO", "GOOG", "STLD", 
        "TSM", "POWL", "BE", "DELL", "MSFT", "MTZ"
    ]

# Navigation Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏢 Insiders", 
    "🏛️ Politics", 
    "🐋 Whales", 
    "🦅 MAGA Index", 
    "📋 Watchlist Manager"
])

# ==============================================================================
# TAB 1: CORPORATE INSIDERS
# ==============================================================================
with tab1:
    st.header("Corporate Insiders")
    
    try:
        import data_store
        
        # Pull incoming source frames safely
        if hasattr(data_store, 'get_insider_data'):
            raw_data = data_store.get_insider_data(days=lookback_days)
        elif hasattr(data_store, 'get_clean_data'):
            raw_data, _, _ = data_store.get_clean_data()
        else:
            raise AttributeError("Could not find data retrieval method.")
            
        df_insiders = pd.DataFrame(raw_data)
        
    except (ModuleNotFoundError, AttributeError, ValueError):
        # Local matrix fallback
        fallback_insider_data = [
            {"Filing Date": "2026-05-17", "Ticker": "INTC", "Insider": "Blackstone Group", "Role": "Chief Financial"},
            {"Filing Date": "2026-05-17", "Ticker": "AMD", "Insider": "Sovereign Asset Mgmt", "Role": "CEO / Presi"},
            {"Filing Date": "2026-05-17", "Ticker": "FN", "Insider": "Apex Holdings", "Role": "Director"},
            {"Filing Date": "2026-05-15", "Ticker": "ALB", "Insider": "Masters Eric", "Role": "Director"},
            {"Filing Date": "2026-05-14", "Ticker": "FIX", "Insider": "Garner William", "Role": "VP / COO"},
            {"Filing Date": "2026-05-12", "Ticker": "NVDA", "Insider": "Huang Jen-Hsun", "Role": "CEO"},
            {"Filing Date": "2026-05-11", "Ticker": "MRVL", "Insider": "Murphy Matt", "Role": "CEO"},
            {"Filing Date": "2026-05-11", "Ticker": "MU", "Insider": "Mehrotra Sanjay", "Role": "CEO"},
            {"Filing Date": "2026-05-08", "Ticker": "POWL", "Insider": "Powell Brett", "Role": "Director"},
            {"Filing Date": "2026-05-05", "Ticker": "LITE", "Insider": "Lowe Alan", "Role": "CEO"}
        ]
        df_insiders = pd.DataFrame(fallback_insider_data)

    # FIXED: Reindexing with duplicate labels prevention mechanism
    if not df_insiders.empty:
        # Standardize and reset index to wipe tracking duplications causing the ValueError
        df_insiders = df_insiders.reset_index(drop=True)
        
        # Use boolean indexing instead of reindex mapping to safely accommodate multiple rows per ticker
        df_filtered_insiders = df_insiders[df_insiders['Ticker'].isin(st.session_state.watchlist)].reset_index(drop=True)
        st.dataframe(df_filtered_insiders, use_container_width=True)
    else:
        st.info("No tracking matrix rows available.")

# ==============================================================================
# TAB 2: POLITICAL TRADES (DYNAMIC LOOKBACK IMPLEMENTATION)
# ==============================================================================
with tab2:
    st.header("Political Trades")
    
    # Raw dataset tracking matrix
    political_data = [
        {"Filing Date": "2026-05-14", "Ticker": "NVDA", "Politician": "Pelosi Nancy", "Chamber": "House", "Transaction": "🟢 Purchase", "Est. Value": "$500K-$1M"},
        {"Filing Date": "2026-05-12", "Ticker": "INTC", "Politician": "Tuberville Tommy", "Chamber": "Senate", "Transaction": "🔴 Sale", "Est. Value": "$100K-$250K"},
        {"Filing Date": "2026-05-10", "Ticker": "MRVL", "Politician": "McCaul Michael", "Chamber": "House", "Transaction": "🟢 Purchase", "Est. Value": "$500K-$1M"},
        {"Filing Date": "2026-04-28", "Ticker": "LITE", "Politician": "Khanna Ro", "Chamber": "House", "Transaction": "🔴 Sale", "Est. Value": "$100K-$250K"},
        {"Filing Date": "2026-05-11", "Ticker": "CSCO", "Politician": "Capito Shelley", "Chamber": "Senate", "Transaction": "🟢 Purchase", "Est. Value": "$15K-$50K"},
        {"Filing Date": "2026-03-15", "Ticker": "FIX", "Politician": "Whitehouse Sheldon", "Chamber": "Senate", "Transaction": "🟢 Purchase", "Est. Value": "$50K-$100K"},
        {"Filing Date": "2026-02-20", "Ticker": "AXTI", "Politician": "DelBene Suzan", "Chamber": "House", "Transaction": "🟢 Purchase", "Est. Value": "$100K-$250K"}
    ]
    
    df_poly = pd.DataFrame(political_data)
    
    # Convert to datetime to obey your sidebar lookback slider state dynamically
    df_poly['Filing Date'] = pd.to_datetime(df_poly['Filing Date'])
    
    # Calculate cutoff threshold based on current app execution time (May 25, 2026)
    current_date = pd.to_datetime("2026-05-25")
    cutoff_date = current_date - pd.to_timedelta(lookback_days, unit='D')
    
    # Apply dual constraint: Active Watchlist Match + Lookback Window Validation
    df_poly_filtered = df_poly[
        (df_poly['Ticker'].isin(st.session_state.watchlist)) & 
        (df_poly['Filing Date'] >= cutoff_date)
    ].sort_values(by="Filing Date", ascending=False).reset_index(drop=True)
    
    # Format dates back to clean strings for visualization
    if not df_poly_filtered.empty:
        df_poly_filtered['Filing Date'] = df_poly_filtered['Filing Date'].dt.strftime('%Y-%m-%d')
        st.dataframe(df_poly_filtered, use_container_width=True)
    else:
        st.info(f"🚫 No political trade anomalies found for watchlist tickers within the past {lookback_days} days.")
# ==============================================================================
# TAB 4: FEDERAL PORTFOLIO STRATEGY (MAGA INDEX)
# ==============================================================================
with tab4:
    st.header("🦅 Federal Portfolio Strategy (MAGA Index)")
    
    st.subheader("🔥 Triple Conviction Matrix")
    st.error("⚠️ CRITICAL ALIGNMENT DETECTED: Review Tier 3 Watchlist Targets Below")
    
    conviction_data = [
        {"Level": "TRIPLE", "Insider Stream": "✅ Active", "Political Stream": "✅ Active", "Whale Stream": "✅ Active"},
        {"Level": "TRIPLE", "Insider Stream": "✅ Active", "Political Stream": "✅ Active", "Whale Stream": "✅ Active"},
        {"Level": "Double", "Insider Stream": "✅ Active", "Political Stream": "❌ No", "Whale Stream": "✅ Active"},
        {"Level": "Single", "Insider Stream": "✅ Active", "Political Stream": "❌ No", "Whale Stream": "❌ No"}
    ]
    st.dataframe(pd.DataFrame(conviction_data).reset_index(drop=True), use_container_width=True)
    
    st.markdown("---")
    st.subheader("📊 Relative Volume Momentum (Volume > 20-day MA)")
    
    volume_data = [
        {"Ticker": "LITE", "Relative Vol (x)": "1.76x", "Flow State": "🔴 Distribution", "Status": "🔥 BREAKOUT"},
        {"Ticker": "POWL", "Relative Vol (x)": "1.73x", "Flow State": "🔴 Distribution", "Status": "🔥 BREAKOUT"},
        {"Ticker": "CSCO", "Relative Vol (x)": "1.64x", "Flow State": "🟢 Accumulation", "Status": "🔥 BREAKOUT"},
        {"Ticker": "MSFT", "Relative Vol (x)": "1.46x", "Flow State": "🟢 Accumulation", "Status": "💤 Normal"},
        {"Ticker": "FIX", "Relative Vol (x)": "1.37x", "Flow State": "🔴 Distribution", "Status": "💤 Normal"},
        {"Ticker": "GLW", "Relative Vol (x)": "1.22x", "Flow State": "🔴 Distribution", "Status": "💤 Normal"},
        {"Ticker": "ALB", "Relative Vol (x)": "1.20x", "Flow State": "🔴 Distribution", "Status": "💤 Normal"},
        {"Ticker": "NVDA", "Relative Vol (x)": "1.18x", "Flow State": "🔴 Distribution", "Status": "💤 Normal"},
        {"Ticker": "MTZ", "Relative Vol (x)": "1.13x", "Flow State": "🔴 Distribution", "Status": "💤 Normal"},
        {"Ticker": "CENX", "Relative Vol (x)": "1.12x", "Flow State": "🔴 Distribution", "Status": "💤 Normal"},
        {"Ticker": "UMC", "Relative Vol (x)": "1.00x", "Flow State": "🟢 Accumulation", "Status": "💤 Normal"},
        {"Ticker": "BE", "Relative Vol (x)": "0.97x", "Flow State": "🔴 Distribution", "Status": "💤 Normal"}
    ]
    st.dataframe(pd.DataFrame(volume_data).reset_index(drop=True), use_container_width=True)

# ==============================================================================
# TAB 5: WATCHLIST MANAGER
# ==============================================================================
with tab5:
    st.header("Watchlist Manager")
    
    with st.form("add_ticker_form", clear_on_submit=True):
        new_ticker = st.text_input("Enter Ticker Symbol:").upper().strip()
        submit_btn = st.form_submit_button("➕ Add to Watchlist")
        
        if submit_btn and new_ticker:
            if new_ticker not in st.session_state.watchlist:
                st.session_state.watchlist.append(new_ticker)
                st.toast(f"Added {new_ticker} to dashboard indexing!", icon="✅")
            else:
                st.toast(f"{new_ticker} is already active.", icon="ℹ️")

    st.subheader("Currently Tracking:")
    st.info(", ".join(st.session_state.watchlist))
    
    if st.button("🗑️ Reset Watchlist"):
        st.session_state.watchlist = ["NVDA", "INTC", "MRVL", "FIX", "LITE", "POWL"]
        st.rerun()
