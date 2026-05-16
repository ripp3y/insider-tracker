import streamlit as st
import pandas as pd
import requests
import warnings
from io import StringIO
import data_store

warnings.filterwarnings("ignore")
st.set_page_config(page_title="Asymmetry", page_icon="👁️‍🗨️", layout="wide")

st.title("👁️‍🗨️ Asymmetry")
st.caption("Alpha Tracking Dashboard")

# 1. INITIALIZE WATCHLIST FROM QUERY PARAMETERS
if "watchlist" not in st.session_state:
    qp = st.query_params
    if "list" in qp:
        st.session_state.watchlist = [t.strip().upper() for t in qp["list"].split(",") if t.strip()]
    else:
        st.session_state.watchlist = ["NVDA", "INTC", "MRVL", "FIX", "ALB", "LITE"]

# Keep query params pinned to current state
st.query_params["list"] = ",".join(st.session_state.watchlist)
wl = st.session_state.watchlist

# 2. DEFINENSIVE DATA RETRIEVAL ENGINE
@st.cache_data(ttl=300)
def get_clean_data(current_watchlist):
    # Always declare baselines first to prevent NameErrors
    ins_df = pd.DataFrame(data_store.get_insider_data_raw())
    poly_df = pd.DataFrame(data_store.get_fallback_political_data())
    whale_df = pd.DataFrame(data_store.get_institutional_data_raw())
    
    # Standardize 'Ticker' across all static sources
    for df in [ins_df, poly_df, whale_df]:
        if not df.empty and "Ticker" in df.columns:
            df["Ticker"] = df["Ticker"].astype(str).str.upper().str.strip()

    # Attempt dynamic live Congress feed sync
    try:
        url = "https://raw.githubusercontent.com/thefuzzlemind/free-congress-stock-data/main/data/latest_trades.csv"
        r = requests.get(url, timeout=3)
        if r.status_code == 200 and len(r.text) > 100:
            df_c = pd.read_csv(StringIO(r.text))
            df_c.columns = [str(c).strip().lower() for c in df_c.columns]
            
            t_col = next((c for c in df_c.columns if c in ["ticker", "symbol"]), None)
            n_col = next((c for c in df_c.columns if c in ["politician", "representative", "name"]), None)
            v_col = next((c for c in df_c.columns if c in ["amount", "range"]), None)
            ty_col = next((c for c in df_c.columns if c in ["type", "transaction"]), None)
            
            if t_col and n_col:
                df_c[t_col] = df_c[t_col].astype(str).str.upper().str.strip()
                df_fil = df_c[df_c[t_col].isin(current_watchlist)].copy()
                if not df_fil.empty:
                    poly_df = pd.DataFrame({
                        "Filing Date": "Live Feed",
                        "Politician": df_fil[n_col].astype(str).str.title(),
                        "Chamber": "Congress",
                        "Ticker": df_fil[t_col],
                        "Type": df_fil[ty_col].fillna("Purchase").apply(lambda x: "🔴 Sale" if "sel" in str(x).lower() else "🟢 Purchase"),
                        "Amount Range": df_fil[v_col].fillna("$15k-$50k"),
                        "Numeric Max": 50000,
                        "Sector": "Infrastructure / Tech"
                    })
    except:
        pass # Gracefully fall back to local store data if network drops
        
    # Filter everything down strictly to watchlist matches
    out_ins = ins_df[ins_df["Ticker"].isin(current_watchlist)] if not ins_df.empty else ins_df
    out_poly = poly_df[poly_df["Ticker"].isin(current_watchlist)] if not poly_df.empty else poly_df
    out_whale = whale_df[whale_df["Ticker"].isin(current_watchlist)] if not whale_df.empty else whale_df
        
    return out_ins, out_poly, out_whale

# Execute data assembly loop
df_insider, df_poly, df_whale = get_clean_data(wl)

# 3. CORE FILTERS (SIDEBAR)
st.sidebar.header("🐋 Core Filters")
min_insider = st.sidebar.slider("Min Insider Value ($)", 0, 1500000, 0, 50000)

if not df_insider.empty and "Value ($)" in df_insider.columns:
    df_insider = df_insider[df_insider["Value ($)"].abs() >= min_insider]

# 4. VIEWPORTS AND TABS
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
    
    # Corrected native method: form_submit_button
    with st.form("add_ticker_form", clear_on_submit=True):
        new_tk = st.text_input("Enter Ticker Symbol:").upper().strip()
        submitted = st.form_submit_button("➕ Add to Watchlist")
        
    if submitted and new_tk:
        if new_tk not in st.session_state.watchlist:
            st.session_state.watchlist.append(new_tk)
            st.rerun()
            
    st.write("### Currently Tracking:")
    st.info(", ".join(st.session_state.watchlist))
    
    if st.button("🗑️ Reset Watchlist"):
        st.session_state.watchlist = ["NVDA", "INTC", "MRVL", "FIX", "ALB", "LITE"]
        st.rerun()

