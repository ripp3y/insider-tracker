import streamlit as st
import pandas as pd
import warnings
import data_store

warnings.filterwarnings("ignore")
st.set_page_config(page_title="Asymmetry", page_icon="👁️‍🗨️", layout="wide")

st.title("👁️‍🗨️ Asymmetry")
st.caption("Alpha Tracking Dashboard")

DEFAULT_TICKERS = ["NVDA", "INTC", "MRVL", "FIX", "ALB", "LITE"]

# --- URL QUERY PARAM CONTROL ---
qp = st.query_params
if "list" in qp and qp["list"].strip():
    current_wl = [t.strip().upper() for t in qp["list"].split(",") if t.strip()]
else:
    current_wl = DEFAULT_TICKERS.copy()
    st.query_params["list"] = ",".join(current_wl)

st.session_state.watchlist = current_wl
wl = st.session_state.watchlist


# --- DATA CACHING & NORMALIZATION ENGINE ---
@st.cache_data(ttl=300)
def get_clean_data(watchlist_symbols):
    try:
        df_i = pd.DataFrame(data_store.get_insider_data_raw(watchlist_symbols))
    except TypeError:
        df_i = pd.DataFrame(data_store.get_insider_data_raw())

    try:
        df_p = pd.DataFrame(data_store.get_fallback_political_data(watchlist_symbols))
    except TypeError:
        df_p = pd.DataFrame(data_store.get_fallback_political_data())

    try:
        df_w = pd.DataFrame(data_store.get_institutional_data_raw(watchlist_symbols))
    except TypeError:
        df_w = pd.DataFrame(data_store.get_institutional_data_raw())

    # Standardize 'Ticker' columns safely across all files
    for df in [df_i, df_p, df_w]:
        if df is not None and not df.empty:
            t_col = next((c for c in df.columns if str(c).lower() in ["ticker", "symbol"]), None)
            if t_col:
                df.rename(columns={t_col: "Ticker"}, inplace=True)
                df["Ticker"] = df["Ticker"].astype(str).str.strip().str.upper()

    return df_i, df_p, df_w

# Extract raw structured matrices (Unfiltered global sets)
raw_insider, raw_poly, raw_whale = get_clean_data(wl)


# --- TRIPLE CONVICTION ALERT MATRIX OVERVIEW (GLOBAL LOOKUP) ---
st.markdown("### 🔥 Triple Conviction Matrix")

# Pull overlapping data from the raw, global datasets before filtering down
insider_set = set(raw_insider["Ticker"].unique()) if not raw_insider.empty else set()
poly_set = set(raw_poly["Ticker"].unique()) if not raw_poly.empty else set()
whale_set = set(raw_whale["Ticker"].unique()) if not raw_whale.empty else set()

matrix_rows = []

for ticker in wl:
    has_insider = ticker in insider_set
    has_poly = ticker in poly_set
    has_whale = ticker in whale_set
    
    score = sum([has_insider, has_poly, has_whale])
    
    if score > 0:
        if score == 3:
            tier = "🚨 Tier 3: TRIPLE"
        elif score == 2:
            tier = "📈 Tier 2: Double"
        else:
            tier = "🔍 Tier 1: Single"
            
        matrix_rows.append({
            "Ticker": ticker,
            "Conviction Level": tier,
            "Insider Stream": "✅ Active" if has_insider else "❌ No",
            "Political Stream": "✅ Active" if has_poly else "❌ No",
            "Whale Stream": "✅ Active" if has_whale else "❌ No",
            "Score": score
        })

if matrix_rows:
    df_matrix = pd.DataFrame(matrix_rows).sort_values(by="Score", ascending=False)
    
    has_tier3 = any(df_matrix["Score"] == 3)
    if has_tier3:
        st.error("⚠️ CRITICAL ALIGNMENT DETECTED: Review Tier 3 Watchlist Targets Below")
        
    st.dataframe(
        df_matrix.drop(columns=["Score"]),
        hide_index=True,
        use_container_width=True
    )
else:
    st.info("No cross-stream activity intersections found on your active watchlist.")

st.markdown("---")


# --- LOCAL WATCHLIST FILTERS FOR INDIVIDUAL TABS ---
df_insider = raw_insider[raw_insider["Ticker"].isin(wl)].copy() if not raw_insider.empty else raw_insider
df_poly = raw_poly[raw_poly["Ticker"].isin(wl)].copy() if not raw_poly.empty else raw_poly
df_whale = raw_whale[raw_whale["Ticker"].isin(wl)].copy() if not raw_whale.empty else raw_whale

# Inject Sector Map descriptions from data_store matrix
for df in [df_insider, df_poly, df_whale]:
    if df is not None and not df.empty and "Ticker" in df.columns:
        df["Sector"] = df["Ticker"].apply(data_store.get_sector)


# --- CORE CONTROL SIDEBAR ---
st.sidebar.header("🐋 Core Filters")
min_insider = st.sidebar.slider("Min Insider Value ($)", 0, 1500000, 0, 50000)

if not df_insider.empty and "Value ($)" in df_insider.columns:
    df_insider = df_insider[df_insider["Value ($)"].abs() >= min_insider]


# --- TABS WORKSPACE UI ---
t1, t2, t3, t4, t5 = st.tabs(["🏢 Insiders", "🏛️ Politics", "🐋 Whales", "🦅 MAGA", "📋 Watchlist"])

with t1:
    st.subheader("Corporate Insiders")
    if not df_insider.empty:
        st.dataframe(
            df_insider, 
            hide_index=True, 
            width="stretch",
            column_config={
                "Value ($)": st.column_config.NumberColumn("Value ($)", format="$%,d")
            }
        )
    else:
        st.info("No active insider entries matching watchlist.")

with t2:
    st.subheader("Political Trades")
    if not df_poly.empty:
        st.dataframe(df_poly, hide_index=True, width="stretch")
    else:
        st.info("No political data found for these assets.")

with t3:
    st.subheader("Whale Blocks")
    if not df_whale.empty:
        st.dataframe(
            df_whale, 
            hide_index=True, 
            width="stretch",
            column_config={
                "Shares Changed": st.column_config.NumberColumn("Shares Changed", format="%,d"),
                "Value ($)": st.column_config.NumberColumn("Value ($)", format="$%,d")
            }
        )
    else:
        st.info("No active block data matching watchlist.")

with t4:
    st.subheader("Federal Portfolio Strategy")
    try:
        st.dataframe(pd.DataFrame(data_store.get_maga_portfolio_data()), hide_index=True, width="stretch")
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
