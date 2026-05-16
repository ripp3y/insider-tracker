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

if "watchlist" not in st.session_state:
    qp = st.query_params
    if "list" in qp:
        st.session_state.watchlist = [t.strip().upper() for t in qp["list"].split(",") if t.strip()]
    else:
        st.session_state.watchlist = ["NVDA", "INTC", "MRVL", "FIX", "ALB", "LITE"]

if st.session_state.watchlist:
    st.query_params["list"] = ",".join(st.session_state.watchlist)

wl = st.session_state.watchlist

@st.cache_data(ttl=300)
def get_clean_data():
    # 1. Initialize Baseline Core Datasets
    ins = pd.DataFrame(data_store.get_insider_data_raw())
    poly = pd.DataFrame(data_store.get_fallback_political_data())
    whale = pd.DataFrame(data_store.get_institutional_data_raw())
    
    # Standardize primary key column across data sources
    for df in [ins, poly, whale]:
        if not df.empty and "Ticker" in df.columns:
            df["Ticker"] = df["Ticker"].astype(str).str.upper().str.strip()

    # 2. Dynamic Live Congress Feed Parse
    try:
        r = requests.get("https://raw.githubusercontent.com/thefuzzlemind/free-congress-stock-data/main/data/latest_trades.csv", timeout=3)
        if r.status_code == 200 and len(r.text) > 100:
            df_c = pd.read_csv(StringIO(r.text))
            df_c.columns = [str(c).strip().lower() for c in df_c.columns]
            
            t_col = next((c for c in df_c.columns if c in ["ticker", "symbol"]), None)
            n_col = next((c for c in df_c.columns if c in ["politician", "representative", "name"]), None)
            v_col = next((c for c in df_c.columns if c in ["amount", "range"]), None)
            ty_col = next((c for c in df_c.columns if c in ["type", "transaction"]), None)
            
            if t_col and n_col:
                df_c[t_col] = df_c[t_col].astype(str).str.upper().str.strip()
                df_fil = df_c[df_c[t_col].isin(wl)].copy()
                if not df_fil.empty:
                    poly = pd.DataFrame({
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
        pass
        
    # 3. Defensive Watchlist Intersect
    ins_f = ins[ins["Ticker"].isin(wl)] if not ins.empty else ins
    poly_f = poly[poly["Ticker"].isin(wl)] if not poly.empty else poly
    whale_f = whale[whale["Ticker"].isin(wl)] if not whale.empty else whale
        
    return ins_f, poly_f, whale_f

    
    try:
        r = requests.get("https://raw.githubusercontent.com/thefuzzlemind/free-congress-stock-data/main/data/latest_trades.csv", timeout=3)
        if r.status_code == 200 and len(r.text) > 100:
            df_c = pd.read_csv(StringIO(r.text))
            df_c.columns = [str(c).strip().lower() for c in df_c.columns]
            t_col = next((c for c in df_c.columns if c in ["ticker", "symbol"]), None)
            n_col = next((c for c in df_c.columns if c in ["politician", "representative", "name"]), None)
            v_col = next((c for c in df_c.columns if c in ["amount", "range"]), None)
            ty_col = next((c for c in df_c.columns if c in ["type", "transaction"]), None)
            
            if t_col and n_col:
                df_c[t_col] = df_c[t_col].astype(str).str.upper().str.strip()
                df_fil = df_c[df_c[t_col].isin(wl)].copy()
                if not df_fil.empty:
                    poly = pd.DataFrame({
                        "Filing Date": "Live Feed",
                        "Politician": df_fil[n_col].astype(str).str.title(),
                        "Chamber": "Congress",
                        "Ticker": df_fil[t_col],
                        "Type": df_fil[ty_col].fillna("Purchase").apply(lambda x: "🔴 Sale" if "sel" in str(x).lower() else "🟢 Purchase"),
                        "Amount Range": df_fil[v_col].fillna("$15k-$50k"),
                        "Numeric Max": 50000,
                        "Sector": "Tech / Industrial"
                    })
    except:
        pass
        
    return ins[ins["Ticker"].isin(wl)], poly[poly["Ticker"].isin(wl)], whale[whale["Ticker"].isin(wl)]

df_insider, df_poly, df_whale = get_clean_data()

st.sidebar.header("🐋 Core Filters")
min_insider = st.sidebar.slider("Min Insider Value ($)", 0, 1500000, 0, 50000)

if not df_insider.empty and "Value ($)" in df_insider.columns:
    df_insider = df_insider[df_insider["Value ($)"].abs() >= min_insider]

t1, t2, t3, t4, t5 = st.tabs(["🏢 Insiders", "🏛️ Politics", "🐋 Whales", "🦅 MAGA", "📋 Watchlist"])

with t1:
    st.subheader("Corporate Insiders")
    if not df_insider.empty:
        st.dataframe(df_insider, hide_index=True, use_container_width=True)
    else:
        st.info("No active insider entries found.")

with t2:
    st.subheader("Political Trades")
    if not df_poly.empty:
        st.dataframe(df_poly[["Filing Date", "Politician", "Ticker", "Type", "Amount Range"]], hide_index=True, use_container_width=True)
    else:
        st.info("No political data found.")

with t3:
    st.subheader("Whale Blocks")
    if not df_whale.empty:
        st.dataframe(df_whale, hide_index=True, use_container_width=True)
    else:
        st.info("No active block data.")

with t4:
    st.subheader("Federal Portfolio Strategy")
    try:
        st.dataframe(pd.DataFrame(data_store.get_maga_portfolio_data()), hide_index=True, use_container_width=True)
    except:
        st.error("Static data feed missing.")

with t5:
    st.subheader("Watchlist Manager")
    new_tk = st.text_input("New Ticker Symbol:").upper().strip()
    if st.button("➕ Add Asset") and new_tk and new_tk not in st.session_state.watchlist:
        st.session_state.watchlist.append(new_tk)
        st.rerun()
    st.write("Tracking:", st.session_state.watchlist)
