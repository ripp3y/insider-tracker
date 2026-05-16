import streamlit as st
import pandas as pd
import warnings
import data_store

warnings.filterwarnings("ignore")
st.set_page_config(page_title="Asymmetry", page_icon="👁️‍🗨️", layout="wide")

st.title("👁️‍🗨️ Asymmetry")
st.caption("Alpha Tracking Dashboard")

DEFAULT_TICKERS = ["NVDA", "INTC", "MRVL", "FIX", "ALB", "LITE"]

# --- URL STORAGE CONTROL ---
qp = st.query_params
if "list" in qp and qp["list"].strip():
    current_wl = [t.strip().upper() for t in qp["list"].split(",") if t.strip()]
else:
    current_wl = DEFAULT_TICKERS.copy()
    st.query_params["list"] = ",".join(current_wl)

st.session_state.watchlist = current_wl
wl = st.session_state.watchlist


# --- DYNAMIC DATA RETRIEVAL ENGINE ---
@st.cache_data(ttl=300)
def get_clean_data(watchlist_symbols):
    # Pass the live watchlist directly down into your data_store functions
    try:
        df_i = pd.DataFrame(data_store.get_insider_data_raw(watchlist_symbols))
    except TypeError:
        # Fallback if the data_store function doesn't accept arguments yet
        df_i = pd.DataFrame(data_store.get_insider_data_raw())

    try:
        df_p = pd.DataFrame(data_store.get_fallback_political_data(watchlist_symbols))
    except TypeError:
        df_p = pd.DataFrame(data_store.get_fallback_political_data())

    try:
        df_w = pd.DataFrame(data_store.get_institutional_data_raw(watchlist_symbols))
    except TypeError:
        df_w = pd.DataFrame(data_store.get_institutional_data_raw())

    # Standardize 'Ticker' columns safely
    for df in [df_i, df_p, df_w]:
        if df is not None and not df.empty:
            t_col = next((c for c in df.columns if str(c).lower() in ["ticker", "symbol"]), None)
            if t_col:
                df.rename(columns={t_col: "Ticker"}, inplace=True)
                df["Ticker"] = df["Ticker"].astype(str).str.strip().str.upper()

    return df_i, df_p, df_w

# Run data fetch with the active watchlist
raw_insider, raw_poly, raw_whale = get_clean_data(wl)

# Final filter slice
df_insider = raw_insider[raw_insider["Ticker"].isin(wl)] if not raw_insider.empty else raw_insider
df_poly = raw_poly[raw_poly["Ticker"].isin(wl)] if not raw_poly.empty else raw_poly
df_whale = raw_whale[raw_whale["Ticker"].isin(wl)] if not raw_whale.empty else raw_whale


# --- SIDEBAR ---
st.sidebar.header("🐋 Core Filters")
min_insider = st.sidebar.slider("Min Insider Value ($)", 0, 1500000, 0, 50000)

if not df_insider.empty and "Value ($)" in df_insider.columns:
    df_insider = df_insider[df_insider["Value ($)"].abs() >= min_insider]


# --- TABS UI ---
t1, t2, t3, t4, t5 = st.tabs(["🏢 Insiders", "🏛️ Politics", "🐋 Whales", "🦅 MAGA", "📋 Watchlist"])

with t1:
    st.subheader("Corporate Insiders")
    if not df_insider.empty:
        st.dataframe(df_insider, hide_index=True, use_container_width=True)
    else:
        st.info("No active insider entries matching watchlist.")

with t2:
    st.subheader("Political Trades")
    if not df_poly.empty:
        st.dataframe(df_poly, hide_index=True, use_container_width=True)
    else:
        st.info("No political data found for these assets.")

with t3:
    st.subheader("Whale Blocks")
    if not df_whale.empty:
        st.dataframe(df_whale, hide_index=True, use_container_width=True)
    else:
        st.info("No active block data matching watchlist.")

with t4:
    st.subheader("Federal Portfolio Strategy")
    try:
        st.dataframe(pd.DataFrame(data_store.get_maga_portfolio_data()), hide_index=True, use_container_width=True)
    except:
        st.error("Static data feed offline.")

with t5:
    st.subheader("Watchlist Manager")
    
    with st.form("add_ticker_form", clear_on_submit=True):
        new_tk = st.text_input("Enter Ticker Symbol:").upper().strip()
        submitted = st.form_submit_button("➕ Add to Watchlist")
        
    if submitted and new_tk:
        if new_tk not in st.session_state.watchlist:
            st.session_state.watchlist.append(new_tk)
            st.query_params["list"] = ",".join(st.session_state.watchlist)
            st.rerun()
            
    st.write("### Currently Tracking:")
    st.info(", ".join(st.session_state.watchlist))
    
    if st.button("🗑️ Reset Watchlist"):
        st.session_state.watchlist = DEFAULT_TICKERS.copy()
        st.query_params["list"] = ",".join(st.session_state.watchlist)
        st.rerun()
