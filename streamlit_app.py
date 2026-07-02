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
 def fetch_terminal_data(tickers, timeframe="6mo", rsi_period=14):
    matrix_data = []
    historical_charts = {}
    if not tickers:
        return pd.DataFrame(), {}
        
    try:
        ticker_string = " ".join(tickers)
        data = yf.download(ticker_string, period=timeframe, group_by="ticker", progress=False)
        
        for ticker in tickers:
            df = data[ticker].dropna() if len(tickers) > 1 else data.dropna()
            if df.empty or len(df) < rsi_period:
                continue

            # --- RSI CALCULATION ---
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0))
            loss = (-delta.where(delta < 0, 0))
            
            # Use Wilder's Smoothing
            avg_gain = gain.ewm(com=rsi_period - 1, min_periods=rsi_period).mean()
            avg_loss = loss.ewm(com=rsi_period - 1, min_periods=rsi_period).mean()
            
            rs = avg_gain / avg_loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            historical_charts[ticker] = df[['Close', 'Volume', 'RSI']]
            
            # Get latest values for the matrix
            current_rsi = float(df['RSI'].iloc[-1])
            # ... [rest of your existing logic]
            
            matrix_data.append({
                "Ticker": ticker,
                "RSI": f"{current_rsi:.2f}",
                # ... [other columns]
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
    selected_timeframe = st.radio("Select Terminal Structural Horizon Lookup:", options=["3mo", "6mo"], index=1, horizontal=True)

    with st.spinner(f"Analyzing macro metrics over {selected_timeframe} lines..."):
        df_results, chart_library = fetch_terminal_data(st.session_state.global_watchlist, timeframe=selected_timeframe)

    if not df_results.empty:
        tab1, tab2 = st.tabs(["🔥 Institutional Squeeze Radar", "🏛️ Market Alpha & Flows"])

        with tab1:
            st.markdown("### Systemic Short Exposure & Breakout Matrix")
            squeeze_df = df_results[["Ticker", "Price", "20D High", "Breakout Status", "Whale Vol Ratio", "Squeeze Risk Profile"]]
            def style_squeeze_tab(df):
                styles = pd.DataFrame('', index=df.index, columns=df.columns)
                styles["Squeeze Risk Profile"] = df["Squeeze Risk Profile"].apply(lambda x: "background-color: #4c1d1d; color: #ff9999; font-weight: bold;" if "CRITICAL" in x else "")
                styles["Breakout Status"] = df["Breakout Status"].apply(lambda x: "background-color: #1a3a2a; color: #99ff99;" if "Breakout" in x else "")
                return styles
            st.dataframe(squeeze_df.style.apply(style_squeeze_tab, axis=None), use_container_width=True, hide_index=True)

        with tab2:
            st.markdown("### Multi-Vector Accumulation Matrix")
            flow_df = df_results[["Ticker", "Price", "Institutional Flow", "Situational Awareness (Aschenbrenner)", "Hedge Fund Positioning", "Executive/Capitol Disclosures"]]
            def style_flow_tab(df):
                styles = pd.DataFrame('', index=df.index, columns=df.columns)
                styles["Institutional Flow"] = df["Institutional Flow"].apply(lambda x: "background-color: #0f2d4a; color: #99ccff; font-weight: bold;" if "WHALE" in x else "")
                styles["Situational Awareness (Aschenbrenner)"] = df["Situational Awareness (Aschenbrenner)"].apply(lambda x: "background-color: #1a3a2a; color: #99ff99;" if "Long" in x else ("background-color: #4a1515; color: #ff9999;" if "Put" in x else ""))
                styles["Hedge Fund Positioning"] = df["Hedge Fund Positioning"].apply(lambda x: "background-color: #3b3613; color: #ffea75;" if "Activist" in x else ("background-color: #113836; color: #7efce6;" if "Momentum" in x else ("background-color: #381111; color: #fc7e7e;" if "Short" in x else "")))
                styles["Executive/Capitol Disclosures"] = df["Executive/Capitol Disclosures"].apply(lambda x: "background-color: #3d1b40; color: #f2a2f5; font-weight: bold;" if "Active" in x else "")
                return styles
            st.dataframe(flow_df.style.apply(style_flow_tab, axis=None), use_container_width=True, hide_index=True)

        # --- 5. THE VISUAL CHART MATRIX OVERLAY ---
        st.markdown("---")
        st.markdown("### 📈 Real-Time Matrix Terminal Visualizer")
        
        current_watchlist = st.session_state.global_watchlist
        if st.session_state.selected_chart_ticker not in current_watchlist:
            st.session_state.selected_chart_ticker = current_watchlist[0] if current_watchlist else "NVDA"
            
        active_ticker = st.selectbox("Select Target Vector Focus to Plot:", options=current_watchlist, index=current_watchlist.index(st.session_state.selected_chart_ticker) if current_watchlist else 0)
        st.session_state.selected_chart_ticker = active_ticker

        if active_ticker in chart_library:
            ticker_data = chart_library[active_ticker]
            
            # --- DYNAMIC TRAILING STOP LOGIC ---
            df_atr = ticker_data.copy()
            df_atr['Volatility_Band'] = df_atr['Close'].rolling(window=14).std() * 2.5
            df_atr['Trailing_Stop_Floor'] = df_atr['Close'] - df_atr['Volatility_Band']
            
            current_close = float(df_atr['Close'].iloc[-1])
            current_floor = float(df_atr['Trailing_Stop_Floor'].iloc[-1])
            recommended_pct = ((current_close - current_floor) / current_close) * 100
            
            st.metric(label=f"🛡️ Dynamic Volatility Trailing Stop ({active_ticker})", value=f"${current_floor:.2f}", delta=f"Set Stop at -{recommended_pct:.1f}% from peak")
            st.caption("This floor automatically widens during high-velocity institutional squeezes to prevent premature shakeouts.")

            st.line_chart(ticker_data['Close'], color="#00ffcc")
            st.bar_chart(ticker_data['Volume'], color="#1f77b4")

    st.write("### 🪓 Matrix Component Control")
    cols = st.columns(min(len(st.session_state.global_watchlist), 4))
    for idx, ticker in enumerate(list(st.session_state.global_watchlist)):
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
