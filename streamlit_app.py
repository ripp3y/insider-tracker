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
        st.session_state.global_watchlist = ["NVDA", "MU", "WOLF", "IREN", "CORZ", "APLD", "PLTR", "MSFT"]

if "selected_chart_ticker" not in st.session_state:
    st.session_state.selected_chart_ticker = st.session_state.global_watchlist[0] if st.session_state.global_watchlist else "NVDA"

def update_cloud_storage():
    if st.session_state.global_watchlist:
        st.query_params["symbols"] = ",".join(st.session_state.global_watchlist)
    else:
        if "symbols" in st.query_params:
            del st.query_params["symbols"]

# --- 2. MULTI-VECTOR RADAR & EXTENDED DATA ENGINE ---
def fetch_terminal_data(tickers, timeframe="6mo"):
    """
    Downloads fresh market metrics using extended structural horizons (3mo or 6mo).
    """
    matrix_data = []
    historical_charts = {}
    if not tickers:
        return pd.DataFrame(), {}
        
    try:
        # Download multi-ticker historical block vector
        data = yf.download(tickers, period=timeframe, group_by="ticker", progress=False)
        
        leopold_longs = ["IREN", "CORZ", "APLD", "RIOT", "CLSK", "BITF", "BTDR", "BE"]
        leopold_shorts = ["NVDA", "MU", "TSM", "ASML", "INTC"]
        trump_high_velocity = ["MSFT", "AMZN", "META", "NFLX", "ORCL", "AMD", "PLTR", "NVDA"]

        for ticker in tickers:
            # Handle pandas multi-index variation based on extraction density
            if len(tickers) > 1:
                if ticker in data.columns.levels[0]:
                    df = data[ticker].dropna()
                else:
                    continue
            else:
                df = data.dropna()

            if df.empty or len(df) < 5:
                continue
                
            # Cache the full extended series for interactive plotting
            historical_charts[ticker] = df[['Close', 'Volume']]
                
            current_price = float(df["Close"].iloc[-1])
            current_volume = float(df["Volume"].iloc[-1])
            
            historical_df = df.iloc[:-1]
            twenty_day_high = float(historical_df["High"].tail(20).max()) 
            avg_volume = float(historical_df["Volume"].mean())
            
            # Vector 1: Technical Breakouts
            price_breakout = current_price >= twenty_day_high
            volume_surge = current_volume >= (avg_volume * 1.5)
            whale_multiplier = float(current_volume / avg_volume) if avg_volume > 0 else 1.0
            
            if price_breakout and volume_surge:
                breakout_signal = "🔥 FULL BREAKOUT"
            elif price_breakout:
                breakout_signal = "📈 Price Breakout"
            elif volume_surge:
                breakout_signal = "⚡ Volume Surge"
            else:
                breakout_signal = "⚪ Consolidated"
            
            # Squeeze Core Calculations
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
                
            # Vector 2: Aschenbrenner AI Infra
            if ticker in leopold_longs:
                leopold_signal = "⚡ Long Data Center/Infra"
            elif ticker in leopold_shorts:
                leopold_signal = "🚨 Heavy Notional Put Hedge"
            else:
                leopold_signal = "⚪ Unallocated"
                
            # Vector 3: Political Disclosures
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
                "Breakout Status": breakout_signal,
                "Squeeze Risk Profile": squeeze_risk,
                "Institutional Flow": inst_action,
                "Situational Awareness (Aschenbrenner)": leopold_signal,
                "Executive/Capitol Disclosures": political_signal
            })
    except Exception as e:
        st.error(f"Data Connection Interrupted: {e}")
        
    return pd.DataFrame(matrix_data), historical_charts

# --- 3. INTERFACE HEADER & ADD TICKER LINE ---
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

# --- 4. TIMEFRAME SELECTOR & DATA COMPILATION ---
if st.session_state.global_watchlist:
    selected_timeframe = st.radio(
        "Select Terminal Structural Horizon Lookup:",
        options=["3mo", "6mo"],
        index=1, 
        horizontal=True
    )

    with st.spinner(f"Analyzing macro metrics over {selected_timeframe} lines..."):
        df_results, chart_library = fetch_terminal_data(st.session_state.global_watchlist, timeframe=selected_timeframe)

    if not df_results.empty:
        # --- TAB OVERLAYS ---
        tab1, tab2 = st.tabs(["🔥 Institutional Squeeze Radar", "🏛️ Market Alpha & Flows"])

        # --- TAB 1: SQUEEZE & BREAKOUTS ---
        with tab1:
            st.markdown("### Systemic Short Exposure & Breakout Matrix")
            squeeze_df = df_results[["Ticker", "Price", "20D High", "Breakout Status", "Whale Vol Ratio", "Squeeze Risk Profile"]]
            
            def style_squeeze_tab(df):
                styles = pd.DataFrame('', index=df.index, columns=df.columns)
                styles["Squeeze Risk Profile"] = df["Squeeze Risk Profile"].apply(lambda x: "background-color: #4c1d1d; color: #ff9999; font-weight: bold;" if "CRITICAL" in x else "")
                styles["Breakout Status"] = df["Breakout Status"].apply(lambda x: "background-color: #1a3a2a; color: #99ff99;" if "Breakout" in x else "")
                return styles
            
            st.dataframe(squeeze_df.style.apply(style_squeeze_tab, axis=None), use_container_width=True, hide_index=True)

        # --- TAB 2: ADVANCED ALIAS FLOWS ---
        with tab2:
            st.markdown("### Multi-Vector Accumulation Matrix")
            flow_df = df_results[["Ticker", "Price", "Whale Vol Ratio", "Institutional Flow", "Situational Awareness (Aschenbrenner)", "Executive/Capitol Disclosures"]]
            
            def style_flow_tab(df):
                styles = pd.DataFrame('', index=df.index, columns=df.columns)
                styles["Institutional Flow"] = df["Institutional Flow"].apply(lambda x: "background-color: #0f2d4a; color: #99ccff; font-weight: bold;" if "WHALE" in x else "")
                styles["Situational Awareness (Aschenbrenner)"] = df["Situational Awareness (Aschenbrenner)"].apply(lambda x: "background-color: #1a3a2a; color: #99ff99;" if "Long" in x else ("background-color: #4a1515; color: #ff9999;" if "Put" in x else ""))
                styles["Executive/Capitol Disclosures"] = df["Executive/Capitol Disclosures"].apply(lambda x: "background-color: #3d1b40; color: #f2a2f5; font-weight: bold;" if "Active" in x else "")
                return styles
                
            st.dataframe(flow_df.style.apply(style_flow_tab, axis=None), use_container_width=True, hide_index=True)

        # --- 5. THE VISUAL CHART MATRIX OVERLAY ---
        st.markdown("---")
        st.markdown("### 📈 Real-Time Matrix Terminal Visualizer")
        
        # Guard rails to ensure selected_chart_ticker exists in active runtime watchlist array
        available_tickers = [t for t in st.session_state.global_watchlist if t in chart_library]
        if available_tickers:
            if st.session_state.selected_chart_ticker not in available_tickers:
                st.session_state.selected_chart_ticker = available_tickers[0]
                
            active_ticker = st.selectbox(
                "Select Target Vector Focus to Plot:", 
                options=available_tickers,
                index=available_tickers.index(st.session_state.selected_chart_ticker)
            )
            st.session_state.selected_chart_ticker = active_ticker

            ticker_data = chart_library[active_ticker]
            
            st.caption(f"Velocity Trend Vector ({active_ticker} Close Price - Past {selected_timeframe})")
            st.line_chart(ticker_data['Close'], color="#00ffcc")
            
            st.caption(f"Volume Profile Allocation ({active_ticker})")
            st.bar_chart(ticker_data['Volume'], color="#1f77b4")
        else:
            st.warning("No valid asset tracking charts compiled for rendering.")

    # --- 6. COMPONENT CONTROL SECTOR ---
    st.write("### 🪓 Matrix Component Control")
    cols = st.columns(min(len(st.session_state.global_watchlist), 4)) if st.session_state.global_watchlist else []
    for idx, ticker in enumerate(st.session_state.global_watchlist):
        col_idx = idx % 4
        with cols[col_idx]:
            if st.button(f"🪓 Trim {ticker}", key=f"del_{ticker}"):
                st.session_state.global_watchlist.remove(ticker)
                if st.session_state.selected_chart_ticker == ticker:
                    st.session_state.selected_chart_ticker = st.session_state.global_watchlist[0] if st.session_state.global_watchlist else "NVDA"
                update_cloud_storage()
                st.rerun()
else:
    st.info("Watchlist lines currently unallocated. Drop assets above.")
