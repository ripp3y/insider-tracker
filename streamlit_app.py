import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. INITIALIZATION & CLOUD/URL SYNC ---
query_params = st.query_params

if "global_watchlist" not in st.session_state:
    if "symbols" in query_params:
        st.session_state.global_watchlist = [s.strip().upper() for s in query_params["symbols"].split(",") if s.strip()]
    else:
        # Default Institutional Matrix
        st.session_state.global_watchlist = ["SMH", "SOXX", "WOLF", "LITE", "FORM", "SKYT", "NVDA", "MU"]

def update_cloud_storage():
    """Syncs the current global_watchlist back to the browser URL."""
    if st.session_state.global_watchlist:
        st.query_params["symbols"] = ",".join(st.session_state.global_watchlist)
    else:
        if "symbols" in st.query_params:
            del st.query_params["symbols"]

# --- 2. THE BREAKOUT SCANNER ENGINE ---
def scan_breakouts(tickers):
    """Parses historical data to identify critical price and volume breakout triggers."""
    breakout_data = []
    if not tickers:
        return breakout_data
        
    try:
        # Pull 1 month of daily data to calculate baseline averages and highs
        data = yf.download(tickers, period="1mo", group_by="ticker", progress=False)
        
        for ticker in tickers:
            # Handle single ticker vs multiple ticker DataFrame structures from yfinance
            df = data[ticker] if len(tickers) > 1 else data
            df = df.dropna()
            if df.empty or len(df) < 5:
                continue
                
            current_price = df["Close"].iloc[-1]
            current_volume = df["Volume"].iloc[-1]
            
            # Historical baselines (excluding the current day)
            historical_df = df.iloc[:-1]
            twenty_day_high = historical_df["High"].max()
            avg_volume = historical_df["Volume"].mean()
            
            # Breakout Conditions
            price_breakout = current_price >= twenty_day_high
            volume_surge = current_volume >= (avg_volume * 1.5)
            
            status = "⚪ Consolidated"
            if price_breakout and volume_surge:
                status = "🔥 FULL BREAKOUT"
            elif price_breakout:
                status = "📈 Price Breakout"
            elif volume_surge:
                status = "⚡ Volume Surge"
                
            breakout_data.append({
                "Ticker": ticker,
                "Price": f"${current_price:.2f}",
                "20D High": f"${twenty_day_high:.2f}",
                "Vol Surge": f"{(((current_volume/avg_volume) - 1) * 100):+.1f}%",
                "Signal": status
            })
    except Exception as e:
        st.error(f"Data Fetch Interrupted: {e}")
        
    return pd.DataFrame(breakout_data)

# --- 3. INTERFACE ENGINE ---
st.markdown("## 🦅 Rebel Terminal Watchlist & Breakout Scanner")
st.caption("Synchronized to Streamlit Cloud URL State")

# Form to safely add new tickers
with st.form(key="add_ticker_form", clear_on_submit=True):
    new_ticker = st.text_input("Enter Ticker Symbol (e.g., SMCI, POWL):").strip().upper()
    submit_button = st.form_submit_button(label="⚡ Add to Watchlist")
    
    if submit_button and new_ticker:
        if new_ticker not in st.session_state.global_watchlist:
            st.session_state.global_watchlist.append(new_ticker)
            update_cloud_storage()
            st.toast(f"Added {new_ticker} to cloud matrix!", icon="✅")
            st.rerun()
        else:
            st.toast(f"{new_ticker} is already active.", icon="ℹ️")

# --- 4. DISPLAY REAL-TIME RADAR ---
if st.session_state.global_watchlist:
    st.write("### 🚨 Active Breakout Matrix")
    
    with st.spinner("Parsing institutional order blocks..."):
        df_results = scan_breakouts(st.session_state.global_watchlist)
        
    if not df_results.empty:
        # Highlight breakout rows dynamically
        def highlight_signals(val):
            if "FULL" in val: return "background-color: #4c1d1d; color: #ff9999;"
            if "Price" in val: return "background-color: #1a3a2a; color: #99ff99;"
            if "Volume" in val: return "background-color: #3a3a1a; color: #ffff99;"
            return ""
            
        styled_df = df_results.style.map(highlight_signals, subset=["Signal"])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    # Manage/Trim layout below the dashboard
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
    st.info("Watchlist is currently empty. Add tickers above to activate the radar.")
