import streamlit as st
import pandas as pd
import requests
import warnings
from io import StringIO
from datetime import datetime
import data_store

warnings.filterwarnings("ignore")
st.set_page_config(page_title="Asymmetry", page_icon="👁️‍🗨️", layout="wide")

st.title("👁️‍🗨️ Asymmetry")
st.caption("Alpha Tracking Dashboard")

# 1. WATCHLIST DEFINITION & SYNC
if "watchlist" not in st.session_state:
    qp = st.query_params
    if "list" in qp:
        st.session_state.watchlist = [t.strip().upper() for t in qp["list"].split(",") if t.strip()]
    else:
        st.session_state.watchlist = ["NVDA", "INTC", "MRVL", "FIX", "ALB", "LITE"]

if st.session_state.watchlist:
    st.query_params["list"] = ",".join(st.session_state.watchlist)

wl = st.session_state.watchlist

# 2. COMPACT DATA ENGINE
@st.cache_data(ttl=300)
def get_data():
    # Base Fallback Datasets
    ins = pd.DataFrame(data_store.get_insider_data_raw())
    poly = pd.DataFrame(data_store.get_fallback_political_data())
    whale = pd.DataFrame(data_store.get_institutional_data_raw())
    
    # Try dynamic Congress feed sync
    try:
        r = requests.get("https://raw.githubusercontent.com/thefuzzlemind/free-congress-stock-data/main/data/latest_trades.csv", timeout=3)
        if r.status_code == 200 and len(r.text) > 100:
            df_c = pd.read_csv(StringIO(r.text))
            df_c.columns = [str(c).strip().lower() for c in df_c.columns]
            # Fast map column indices to dynamic fields safely
            t_col = next((c for c in df_c.columns if c in ["ticker", "symbol"]), None)
            n_col = next((c for c in df_c.columns if c in ["politician", "representative", "name"]), None)
            v_col = next((c for c in df_c.columns if c in ["amount", "range"]), None)
            ty_col = next((c for c in df_c.columns if c in ["type", "transaction"]), None)
            
            if t_col and n_col:
                df_c[t_col] = df_c[t_col].astype(str).str.upper().str.strip()
                df_fil = df_c[df_c[t_col].isin(wl)].copy()
                if not df_fil.empty:
                    poly = pd.DataFrame({
                        "Filing Date": datetime.now().strftime("%Y-%m-%d"),
                        "Politician": df_fil[n_col].astype(str).str.title(),
                        "Chamber": "Congress",
                        "Ticker": df_fil[t_col],
                        "Type": df_fil[ty_col].fillna("Purchase").apply(lambda x: "🔴 Sale" if "sel" in str(x).lower() else "🟢 Purchase"),
                        "Amount Range": df_fil[v_col].fillna("$15k-$50k"),
                        "Numeric Max": 50000,
                        "Sector": "Infrastructure / Tech"
                    })
    except:
        pass

    # Ensure clean DateTime handling across blocks
    for df in [ins, poly, whale]:
        if not df.empty and "Filing Date" in df.columns:
            df["Filing Date"] = pd.to_datetime(df["Filing Date"]).dt.strftime("%Y-%m-%d")
            
    return ins[ins["Ticker"].isin(wl)], poly[poly["Ticker"].isin(wl)], whale[whale["Ticker"].isin(wl)]

df_insider, df_poly, df_whale = get_data()

# 3. SIDEBAR CONTROLS
st.sidebar.header("🐋 Filters")
min_insider = st.sidebar.slider("Min Insider $", 0, 1500000, 0, 50000)
min_whale = st.sidebar.slider("Min Whale $M", 0, 600, 0, 10) * 1000000

df_insider = df_insider[df_insider["Value ($)"].abs() >= min_insider] if not df_insider.empty else df_insider
df_whale = df_whale[df_whale["Value ($)"].abs() >= min_whale] if not df_whale.empty else df_whale

# Sector Multi-Chart Aggregator
if not df_insider.empty:
    st.sidebar.bar_chart(df_insider["Sector"].value_counts())

# 4. FLAT ALERT GRID (Fixes missing trailing statements)
try:
    set_i = set(df_insider["Ticker"]) if not df_insider.empty else set()
    set_p = set(df_poly["Ticker"]) if not df_poly.empty else set()
    set_w = set(df_whale["Ticker"]) if not df_whale.empty else set()
    triple = set_i.intersection(set_p).intersection(set_w)
except:
    triple = set()

if triple:
    st.error(f"⚡ **Asymmetry Alert: Triple Conviction Matrix detected on {list(triple)}**")

# 5. TAB CONTROL VIEWPORTS
t1, t2, t3, t4, t5 = st.tabs(["🏢 Insiders", "🏛️ Politics", "🐋 Whales", "🦅 MAGA", "📋 Watchlist"])

with t1:
    st.subheader("Corporate Insiders (Form 4)")
    if not df_insider.empty:
        st.metric("Total Insider Volume", f"${df_insider['Value ($)'].abs().sum():,.0f}")
        st.dataframe(df_insider, hide_index=True, use_container_width=True)
    else:
        st.info("No matching insider activity.")

with t2:
    st.subheader("Capitol Hill Transactions")
    if not df_poly.empty:
        st.dataframe(df_poly[["Filing Date", "Politician", "Ticker", "Type", "Amount Range"]], hide_index=True, use_container_width=True)
    else:
        st.info("No active political filings.")

with t3:
    st.subheader("Institutional Whales")
    if not df_whale.empty:
        st.dataframe(df_whale, hide_index=True, use_container_width=True)
    else:
        st.info("No active whale blocks.")

with t4:
    st.subheader("🇺🇸 High-Conviction Federal Portfolio")
    try:
        df_m = pd.DataFrame(data_store.get_maga_portfolio_data())
        st.dataframe(df_m, hide_index=True, use_container_width=True)
    except:
        st.warning("MAGA alpha portfolio engine offline.")

with t5:
    st.subheader("Watchlist Operations")
    new_tk = st.text_input("Add Ticker:").upper().strip()
    if st.button("➕ Add") and new_tk and new_tk not in st.session_state.watchlist:
        st.session_state.watchlist.append(new_tk)
        st.rerun()
        
    st.write("Current Items:", st.session_state.watchlist)
    if st.button("🗑️ Clear All"):
        st.session_state.watchlist = ["NVDA"]
        st.rerun()
