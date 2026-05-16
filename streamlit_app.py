import streamlit as st
import pandas as pd
import requests
import warnings
import os
from io import StringIO
import data_store

warnings.filterwarnings("ignore")
st.set_page_config(page_title="Asymmetry", page_icon="👁️‍🗨️", layout="wide")

st.title("👁️‍🗨️ Asymmetry")
st.caption("Alpha Tracking Dashboard")

# --- PERSISTENT STORAGE MANAGEMENT ---
WATCHLIST_FILE = "watchlist.txt"
DEFAULT_TICKERS = ["NVDA", "INTC", "MRVL", "FIX", "ALB", "LITE"]

def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "r") as f:
            tickers = [line.strip().upper() for line in f.readlines() if line.strip()]
            if tickers:
                return tickers
    return DEFAULT_TICKERS.copy()

def save_watchlist(tickers):
    with open(WATCHLIST_FILE, "w") as f:
        for t in tickers:
            f.write(f"{t}\n")

# Initialize global tracking list
if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_watchlist()

wl = st.session_state.watchlist


# --- FLATTENED DATA ENGINE ---
@st.cache_data(ttl=300)
def get_clean_data():
    try:
        df_i = pd.DataFrame(data_store.get_insider_data_raw())
    except:
        df_i = pd.DataFrame()

    try:
        df_p = pd.DataFrame(data_store.get_fallback_political_data())
    except:
        df_p = pd.DataFrame()

    try:
        df_w = pd.DataFrame(data_store.get_institutional_data_raw())
    except:
        df_w = pd.DataFrame()

    # Standardize uppercase string matches
    if not df_i.empty and "Ticker" in df_i.columns:
        df_i["Ticker"] = df_i["Ticker"].astype(str).str.upper().str.strip()
    if not df_p.empty and "Ticker" in df_p.columns:
        df_p["Ticker"] = df_p["Ticker"].astype(str).str.upper().str.strip()
    if not df_w.empty and "Ticker" in df_w.columns:
        df_w["Ticker"] = df_w["Ticker"].astype(str).str.upper().str.strip()

    return df_i, df_p, df_w

raw_insider, raw_poly, raw_whale = get_clean_data()

# Outer filtering engine
df_insider = raw_insider[raw_insider["Ticker"].isin(wl)] if not raw_insider.empty else raw_insider
df_poly = raw_poly[raw_poly["Ticker"].isin(wl)] if not raw_poly.empty else raw_poly
df_whale = raw_whale[raw_whale["Ticker"].isin(wl)] if not raw_whale.empty else raw_whale


# --- SIDEBAR ---
st.sidebar.header("🐋 Core Filters")
min_insider = st.sidebar.slider("Min Insider Value ($)", 0, 1500000, 0, 50000)

if not df_insider.empty and "Value ($)" in df_insider.columns:
    df_insider = df_insider[df_insider["Value ($)"].abs() >= min_insider]


# --- TABS SYSTEM ---
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
            save_watchlist(st.session_state.watchlist)  # Lock into disk file
            st.rerun()
            
    st.write("### Currently Tracking:")
    st.info(", ".join(st.session_state.watchlist))
    
    if st.button("🗑️ Reset Watchlist"):
        st.session_state.watchlist = DEFAULT_TICKERS.copy()
        save_watchlist(st.session_state.watchlist)  # Lock defaults into disk file
        st.rerun()
