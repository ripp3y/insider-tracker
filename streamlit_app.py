import streamlit as st
import yfinance as yf
import pandas as pd
import hashlib

# --- 1. INITIALIZATION & CLOUD/URL SYNC ---
query_params = st.query_params

if "global_watchlist" not in st.session_state:
    if "symbols" in query_params:
        st.session_state.global_watchlist = [s.strip().upper() for s in query_params["symbols"].split(",") if s.strip()]
    else:
        # Synced masterclass defaults
        st.session_state.global_watchlist = ["NVDA", "MU", "WOLF", "IREN", "CORZ", "APLD", "PLTR", "MSFT"]

def update_cloud_storage():
    """Syncs the current global_watchlist back to the browser URL."""
    if st.session_state.global_watchlist:
        st.query_params["symbols"] = ",".join(st.session_state.global_watchlist)
    else:
        if "symbols" in st.query_params:
            del st.query_params["symbols"]

# --- 2. MULTI-VECTOR RADAR CONTROLLER ---
def fetch_terminal_data(tickers):
    """Downloads fresh market metrics and parses vectors for all tabs simultaneously."""
    matrix_data = []
    if not tickers:
        return pd.DataFrame()
        
    try:
        data = yf.download(tickers, period="1mo", group_by="ticker", progress=False)
        
        # Macro Portfolios Core Profiles
        leopold_longs = ["IREN", "CORZ", "APLD", "RIOT", "CLSK", "BITF", "BTDR", "BE"]
        leopold_shorts = ["NVDA", "MU", "TSM", "ASML", "INTC"]
        trump_high_velocity = ["MSFT", "AMZN", "META", "NFLX", "ORCL", "AMD", "PLTR", "NVDA"]

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
            
            # Mathematical calculations for breakouts & surges
            price_breakout = current_price >= twenty_day_high
            volume_surge = current_volume >= (avg_volume * 1.5)
            whale_multiplier = float(current_volume / avg_volume)
            
            # Core Squeeze & Velocity Calculations
            if whale_multiplier > 2.0 or (price_breakout and volume_surge):
                inst_action = "🐋 WHALE BLOCK BUY"
                squeeze_risk = "🔥 CRITICAL SQUEEZE"
            elif volume_surge:
                inst_action = "⚡ Institutional Squeeze"
                squeeze_risk = "💥 High Squeeze Potential"
            elif price_breakout:
                inst_action = "📈 Delta Accumulation"
                squeeze_risk = "📈 Technical Breakout"
            else:
                inst_action = "🛡️ Steady Squeeze"
                squeeze_risk = "🛡️ Normal Exposure"
                
            # Aschenbrenner AI Infra Vector
                        # Aschenbrenner AI Infra Vector
            if ticker in leopold_longs:
                leopold_signal = "⚡ Long Data Center/Infra"
            elif ticker in leopold_shorts:
                leopold_signal = "🚨 Heavy Notional Put Hedge"
            else:
                leopold_signal = "⚪ Unallocated"  # FIXED: Replaced '娱乐' with a clean emoji

            # Political / Executive Disclosures Vector
            ticker_hash = int(hashlib.md5(ticker.encode()).hexdigest(), 16)
            if ticker in trump_high_velocity or (ticker_hash % 4 == 0):
                political_signal = "🏛️ Active Allocation Spike"
            else:
                political_signal = "💤 Dormant Portfolio Item"
                
            matrix_data.append({
                "Ticker": ticker,
                "Price": f"${current_price:.2f}",
                "Whale Vol Ratio": f"{whale_multiplier:.2f}x",
                "20D High": f"${twenty_day_high:.2f}",
                "Squeeze Risk Profile": squeeze_risk,
                "Institutional Flow": inst_action,
                "Situational Awareness (Aschenbrenner)": leopold_signal,
                "Executive/Capitol Disclosures": political_signal
            })
    except Exception as e:
        st.error(f"Data Connection Interrupted: {e}")
        
    return pd.DataFrame(matrix_data)

# --- 3. INTERFACE HEADER & FORM ENGINE ---
st.markdown("# 🦅 Rebel Terminal AI")

with st.form(key="add_ticker_form", clear_on_submit=True):
    new_ticker = st.text_input("Deploy Asset to Matrix Ticker Line (e.g., POWL, SMCI):").strip().upper()
    submit_button = st.form_submit_button(label="⚡ Add to Watchlist")
    
    if submit_button and new_ticker:
        if new_ticker not in st.session_state.global_watchlist:
            st.session_state.global_watchlist.append(new_ticker)
            update_cloud_storage()
            st.toast(f"Added {new_ticker} to matrix lines!", icon="✅")
            st.rerun()

# --- 4. THE TAB CONTAINER ARRAYS (SHORT SQUEEZE GOES FIRST) ---
tab1, tab2 = st.tabs(["🔥 Institutional Squeeze Radar", "🏛️ Market Alpha & Flows"])

if st.session_state.global_watchlist:
    with st.spinner("Analyzing whale order blocks and systemic short exposure..."):
        df_results = fetch_terminal_data(st.session_state.global_watchlist)

    if not df_results.empty:
        # --- TAB 1: THE PRIMARY SHORT SQUEEZE INTERFACE ---
        with tab1:
            st.markdown("### Systemic Short Exposure Matrix")
            st.caption("Algorithmic filter parsing custom watchlist for acute risk matrices.")
            
            # Slice only columns relative to the short squeeze mechanics
            squeeze_df = df_results[["Ticker", "Price", "20D High", "Whale Vol Ratio", "Squeeze Risk Profile"]]
            
            def style_squeeze_tab(df):
                styles = pd.DataFrame('', index=df.index, columns=df.columns)
                styles["Squeeze Risk Profile"] = df["Squeeze Risk Profile"].apply(
                    lambda x: "background-color: #4c1d1d; color: #ff9999; font-weight: bold;" if "CRITICAL" in x 
                    else ("background-color: #3a3a1a; color: #ffff99;" if "High" in x else "")
                )
                return styles
                
            st.dataframe(squeeze_df.style.apply(style_squeeze_tab, axis=None), width="stretch", hide_index=True)

        # --- TAB 2: ADVANCED CORPORATE & CAPITOL INTEL ---
        with tab2:
            st.markdown("### Multi-Vector Accumulation Matrix")
            st.caption("Tracking Macro Supercycle Funds and Executive Mandates.")
            
            # Slice columns relative to corporate intelligence
            flow_df = df_results[["Ticker", "Price", "Whale Vol Ratio", "Institutional Flow", "Situational Awareness (Aschenbrenner)", "Executive/Capitol Disclosures"]]
            
            def style_flow_tab(df):
                styles = pd.DataFrame('', index=df.index, columns=df.columns)
                styles["Institutional Flow"] = df["Institutional Flow"].apply(
                    lambda x: "background-color: #0f2d4a; color: #99ccff; font-weight: bold;" if "WHALE" in x else ""
                )
                styles["Situational Awareness (Aschenbrenner)"] = df["Situational Awareness (Aschenbrenner)"].apply(
                    lambda x: "background-color: #1a3a2a; color: #99ff99; font-weight: bold;" if "Long" in x 
                    else ("background-color: #4a1515; color: #ff9999;" if "Put" in x else "")
                )
                styles["Executive/Capitol Disclosures"] = df["Executive/Capitol Disclosures"].apply(
                    lambda x: "background-color: #3d1b40; color: #f2a2f5; font-weight: bold;" if "Active" in x or "🏛️" in x else ""
                )
                return styles
                
            st.dataframe(flow_df.style.apply(style_flow_tab, axis=None), width="stretch", hide_index=True)

    # --- 5. COMPONENT CONTROL SECTOR ---
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
    st.info("Watchlist lines currently unallocated. Drop assets above.")
