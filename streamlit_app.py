import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. INITIALIZATION & CLOUD/URL SYNC ---
query_params = st.query_params

if "global_watchlist" not in st.session_state:
    if "symbols" in query_params:
        st.session_state.global_watchlist = [s.strip().upper() for s in query_params["symbols"].split(",") if s.strip()]
    else:
        st.session_state.global_watchlist = ["SMH", "SOXX", "WOLF", "LITE", "FORM", "SKYT"]

def update_cloud_storage():
    """Syncs the current global_watchlist back to the browser URL."""
    if st.session_state.global_watchlist:
        st.query_params["symbols"] = ",".join(st.session_state.global_watchlist)
    else:
        if "symbols" in st.query_params:
            del st.query_params["symbols"]

# --- 2. INTEGRATED WHALE & BREAKOUT RADAR ENGINE ---
def scan_institutional_matrix(tickers):
    """Calculates price velocity and tracks institutional block accumulations."""
    matrix_data = []
    if not tickers:
        return matrix_data
        
    try:
        data = yf.download(tickers, period="1mo", group_by="ticker", progress=False)
        
        for ticker in tickers:
            df = data[ticker] if len(tickers) > 1 else data
            df = df.dropna()
            if df.empty or len(df) < 5:
                continue
                
            current_price = df["Close"].iloc[-1]
            current_volume = df["Volume"].iloc[-1]
            
            historical_df = df.iloc[:-1]
            twenty_day_high = historical_df["High"].max()
            avg_volume = historical_df["Volume"].mean()
            
            # Technical Breakout States
            price_breakout = current_price >= twenty_day_high
            volume_surge = current_volume >= (avg_volume * 1.5)
            
            # Whale Metric
            whale_multiplier = float(current_volume / avg_volume)
            
            # Structural Whale Alerts
            if whale_multiplier > 2.0 or (price_breakout and volume_surge):
                inst_action = "🐋 WHALE BLOCK BUY"
            elif volume_surge:
                inst_action = "⚡ Institutional Squeeze"
            elif price_breakout:
                inst_action = "📈 Delta Accumulation"
            else:
                inst_action = "🛡️ Steady Squeeze"
                
            matrix_data.append({
                "Ticker": ticker,
                "Price": f"${current_price:.2f}",
                "20D High": f"${twenty_day_high:.2f}",
                "Whale Vol Ratio": f"{whale_multiplier:.2f}x",  # FIXED: Moved the 'x' outside the format specifier
                "Institutional Flow": inst_action
            })
    except Exception as e:
        st.error(f"Data Connection Interrupted: {e}")
        
    return pd.DataFrame(matrix_data)

# --- 3. INTERFACE ENGINE ---
st.markdown("## 🦅 Rebel Terminal Watchlist & Institutional Tracker")
st.caption("Synchronized to Streamlit Cloud URL State")

# Dynamic form entry
with st.form(key="add_ticker_form", clear_on_submit=True):
    new_ticker = st.text_input("Add Ticker to Matrix (e.g., PLTR, MU):").strip().upper()
    submit_button = st.form_submit_button(label="⚡ Add to Watchlist")
    
    if submit_button and new_ticker:
        if new_ticker not in st.session_state.global_watchlist:
            st.session_state.global_watchlist.append(new_ticker)
            update_cloud_storage()
            st.toast(f"Added {new_ticker} to cloud matrix!", icon="✅")
            st.rerun()

# --- 4. DISPLAY REAL-TIME MATRIX ---
if st.session_state.global_watchlist:
    st.write("### 🚨 Institutional Accumulation Matrix")
    
    with st.spinner("Analyzing whale order blocks..."):
        df_results = scan_institutional_matrix(st.session_state.global_watchlist)
        
    if not df_results.empty:
        def highlight_whale_flows(val):
            if "WHALE" in val: return "background-color: #0f2d4a; color: #99ccff; font-weight: bold;"
            if "Squeeze" in val: return "background-color: #3a3a1a; color: #ffff99;"
            if "Delta" in val: return "background-color: #1a3a2a; color: #99ff99;"
            return ""
            
        styled_df = df_results.style.map(highlight_whale_flows, subset=["Institutional Flow"])
        st.dataframe(styled_df, width="stretch", hide_index=True)
    
    # Grid item controls
    st.write("### 🪓 Matrix Component Control")
    cols = st.columns(min(len(st.session_state.global_watchlist), 4))
    for idx, ticker in enumerate(st.session_state.global_watchlist):
        col_idx = idx % 4
        with cols[col_idx]:
            if st.button(f"🪓 Trim {ticker}", key=f"del_{ticker}"):
                st.session_state.global_watchlist.remove(ticker)
                update_cloud_storage()
                st.rerun()
else:
    st.info("Watchlist matrix is currently unallocated. Enter tickers above.")
