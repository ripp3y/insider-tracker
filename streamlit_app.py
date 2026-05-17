# streamlit_app.py
import streamlit as st
import pandas as pd
import warnings
import data_store
import json
from urllib.request import Request, urlopen

warnings.filterwarnings("ignore")
st.set_page_config(page_title="Asymmetry", page_icon="👁️‍🗨️", layout="wide")

st.title("👁️‍🗨️ Asymmetry")
st.caption("Alpha Tracking Dashboard")

DEFAULT_TICKERS = ["NVDA", "INTC", "MRVL", "FIX", "ALB", "LITE"]

# --- FIXED URL QUERY PARAM CONTROL ---
if "watchlist" not in st.session_state:
    qp = st.query_params
    if "list" in qp and qp["list"].strip():
        st.session_state.watchlist = [t.strip().upper() for t in qp["list"].split(",") if t.strip()]
    else:
        st.session_state.watchlist = DEFAULT_TICKERS.copy()
        st.query_params["list"] = ",".join(st.session_state.watchlist)

# Bind the working variable directly to the established session state
wl = st.session_state.watchlist


# --- DATA CACHING ENGINE ---
@st.cache_data(ttl=300)
def get_clean_data(watchlist_symbols):
    # Ensure we fall back to everything if the list somehow arrives empty
    symbols = watchlist_symbols if watchlist_symbols else DEFAULT_TICKERS
    
    df_i = pd.DataFrame(data_store.get_insider_data_raw(symbols))
    df_p = pd.DataFrame(data_store.get_fallback_political_data(symbols))
    df_w = pd.DataFrame(data_store.get_institutional_data_raw(symbols))

    for df in [df_i, df_p, df_w]:
        if df is not None and not df.empty:
            t_col = next((c for c in df.columns if str(c).lower() in ["ticker", "symbol"]), None)
            if t_col:
                df.rename(columns={t_col: "Ticker"}, inplace=True)
                df["Ticker"] = df["Ticker"].astype(str).str.strip().str.upper()

    return df_i, df_p, df_w


# --- NATIVE YAHOO FINANCE HISTORICAL VOLUME ENGINE ---
@st.cache_data(ttl=900)
def calculate_native_volume_breakouts(watchlist_tickers):
    symbols = watchlist_tickers if watchlist_tickers else DEFAULT_TICKERS
    volume_data = []
    for ticker in symbols:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=1mo&interval=1d"
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req) as response:
                data = json.loads(response.read().decode())
                
            indicators = data['chart']['result'][0]['indicators']['quote'][0]
            volumes = [v for v in indicators['volume'] if v is not None]
            closes = [c for c in indicators['close'] if c is not None]
            
            if len(volumes) >= 2 and len(closes) >= 2:
                current_vol = float(volumes[-1])
                current_price = float(closes[-1])
                prev_price = float(closes[-2])
                
                historic_volumes = volumes[-21:-1]
                avg_vol_20d = sum(historic_volumes) / len(historic_volumes) if historic_volumes else 0
                
                if avg_vol_20d > 0:
                    vol_ratio = current_vol / avg_vol_20d
                    price_change = ((current_price - prev_price) / prev_price) * 100
                    
                    direction = "🟢 Accumulation" if price_change >= 0 else "🔴 Distribution"
                    status = "🔥 BREAKOUT" if vol_ratio >= 1.5 else "💤 Normal"
                    
                    volume_data.append({
                        "Ticker": ticker,
                        "Vol Ratio": round(vol_ratio, 2),
                        "Flow State": direction,
                        "Status": status,
                        "Price Change": round(price_change, 2)
                    })
        except:
            continue
    return pd.DataFrame(volume_data)


# Populate background matrices safely
raw_insider, raw_poly, raw_whale = get_clean_data(wl)


# --- TRIPLE CONVICTION ALERT MATRIX OVERVIEW ---
st.markdown("### 🔥 Triple Conviction Matrix")

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
    if any(df_matrix["Score"] == 3):
        st.error("⚠️ CRITICAL ALIGNMENT DETECTED: Review Tier 3 Watchlist Targets Below")
    st.dataframe(df_matrix.drop(columns=["Score"]), hide_index=True, use_container_width=True)
else:
    st.info("No cross-stream activity intersections found on your active watchlist.")


# --- LIVE RELATIVE VOLUME METRICS BOARD ---
st.markdown("### 📊 Relative Volume Momentum (Volume > 20-day MA)")
df_volume = calculate_native_volume_breakouts(wl)

if not df_volume.empty:
    df_volume = df_volume.sort_values(by="Vol Ratio", ascending=False)
    st.dataframe(
        df_volume,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Vol Ratio": st.column_config.NumberColumn("Relative Vol (x)", format="%.2fx"),
            "Price Change": st.column_config.NumberColumn("Price Change (%)", format="%.2f%%")
        }
    )
else:
    st.info("Market data feeds loading or currently offline.")

st.markdown("---")

df_insider = raw_insider[raw_insider["Ticker"].isin(wl)].copy() if not raw_insider.empty else raw_insider
df_poly = raw_poly[raw_poly["Ticker"].isin(wl)].copy() if not raw_poly.empty else raw_poly
df_whale = raw_whale[raw_whale["Ticker"].isin(wl)].copy() if not raw_whale.empty else raw_whale

for df in [df_insider, df_poly, df_whale]:
    if df is not None and not df.empty and "Ticker" in df.columns:
        df["Sector"] = df["Ticker"].apply(data_store.get_sector)


# --- CORE SIDEBAR CONTROLS ---
st.sidebar.header("🐋 Core Filters")
min_insider = st.sidebar.slider("Min Insider Value ($)", 0, 1500000, 0, 50000)

if not df_insider.empty and "Value ($)" in df_insider.columns:
    df_insider = df_insider[df_insider["Value ($)"].abs() >= min_insider]


# --- MAIN TABS FRAMEWORK ---
t1, t2, t3, t4, t5 = st.tabs(["🏢 Insiders", "🏛️ Politics", "🐋 Whales", "🦅 MAGA", "📋 Watchlist"])

with t1:
    st.subheader("Corporate Insiders")
    if not df_insider.empty:
        st.dataframe(
            df_insider, 
            hide_index=True, 
            use_container_width=True,
            column_config={"Value ($)": st.column_config.NumberColumn("Value ($)", format="$%,d")}
        )
    else:
        st.info("No active insider entries matching watchlist.")

with t2:
    st.subheader("Political Trades")
    if not df_poly.empty:
        st.dataframe(df_poly, hide_index=True, use_container_width=True)
    else:
        st.info("No political data found for these assets.")

with t3:
    st.subheader("🐋 Institutional Whale Blocks")
    if not df_whale.empty:
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            whale_filter = st.multiselect("Filter by Fund Type:", options=list(df_whale["Type"].unique()), default=list(df_whale["Type"].unique()))
        with col_w2:
            flow_filter = st.multiselect("Filter Flow State:", options=list(df_whale["Change Direction"].unique()), default=list(df_whale["Change Direction"].unique()))
            
        df_whale_filtered = df_whale[df_whale["Type"].isin(whale_filter) & df_whale["Change Direction"].isin(flow_filter)]
        
        if not df_whale_filtered.empty:
            st.dataframe(
                df_whale_filtered.sort_values(by="Value ($)", ascending=False), 
                hide_index=True, 
                use_container_width=True,
                column_config={
                    "Shares Changed": st.column_config.NumberColumn("Shares Δ", format="%,d"),
                    "Value ($)": st.column_config.NumberColumn("Est. Value ($)", format="$%,d"),
                    "Report Date": st.column_config.DateColumn("Filing Date")
                }
            )
        else:
            st.info("No whale blocks found matching the active filters.")
    else:
        st.info("No active whale entries matching your current watchlist tickers.")

with t4:
    st.subheader("🦅 Federal Portfolio Strategy (MAGA Index)")
    maga_raw = data_store.get_live_maga_strategy_data(wl)
    df_maga = pd.DataFrame(maga_raw)
    
    if not df_maga.empty:
        df_maga["Sector"] = df_maga["Ticker"].apply(data_store.get_sector)
        st.dataframe(
            df_maga[["Ticker", "Sector", "Holding Sizing", "Policy Catalyst"]], 
            hide_index=True, 
            use_container_width=True
        )
    else:
        st.info("Track strategic policy-driven assets in the Watchlist tab to map trends.")

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
