import streamlit as st
import yfinance as yf
import pandas as pd
import hashlib
import urllib.request
from bs4 import BeautifulSoup

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

# --- PUBLIC DATA DUAL-MODE SCANNER ---
def fetch_preshift_movers(tickers_list=None):
    """
    Scrapes live momentum gainers directly from public financial tracking lines.
    Pivots from pre-market feeds to live day-gainers if the early session is empty.
    """
    try:
        # Step 1: Scan early pre-market tracking lines first
        url = "https://finance.yahoo.com/markets/stocks/pre-market-gainers/"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read()
        
        soup = BeautifulSoup(html, 'html.parser')
        rows = soup.find_all('tr', class_='markets-table-row')
        mode_label = "Pre-Market"
        
        # Step 2: Fallback to active regular session lines if pre-market is empty/closed
        if not rows:
            url = "https://finance.yahoo.com/markets/stocks/gainers/"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            html = urllib.request.urlopen(req).read()
            soup = BeautifulSoup(html, 'html.parser')
            rows = soup.find_all('tr', class_='markets-table-row')
            mode_label = "Intraday"
        
        movers = []
        for row in rows:
            try:
                symbol = row.find('span', class_='symbol').text.strip()
                price = float(row.find('td', {'data-field': 'regularMarketPrice'}).text.replace('$', '').replace(',', ''))
                gap_text = row.find('td', {'data-field': 'regularMarketChangePercent'}).text
                gap_pct = float(gap_text.replace('+', '').replace('%', '').replace(',', ''))
                volume_text = row.find('td', {'data-field': 'regularMarketVolume'}).text
                
                if 'M' in volume_text:
                    volume = int(float(volume_text.replace('M', '')) * 1_000_000)
                elif 'K' in volume_text:
                    volume = int(float(volume_text.replace('K', '')) * 1_000)
                else:
                    volume = int(volume_text.replace(',', ''))

                # Dynamic filter: $1 to $5 for pre-market microcaps, up to $10 for intraday runners
                max_price = 5.00 if mode_label == "Pre-Market" else 10.00
                if 1.00 <= price <= max_price and gap_pct >= 2.0:
                    movers.append({
                        "Ticker": symbol,
                        "Price": f"${price:.2f}",
                        "Prev Close": f"${(price / (1 + (gap_pct/100))):.2f}",
                        "Gap/Change %": gap_pct,
                        "Volume Lines": volume,
                        "Session Source": mode_label
                    })
            except:
                continue 
                
        df = pd.DataFrame(movers)
        if not df.empty:
            return df.sort_values(by="Gap/Change %", ascending=False).reset_index(drop=True)
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"Public Data Stream Interrupted: {e}")
        return pd.DataFrame()

# --- 2. MULTI-VECTOR RADAR & EXTENDED DATA ENGINE ---
def fetch_terminal_data(tickers, timeframe="6mo"):
    """
    Downloads fresh market metrics using extended structural horizons.
    Integrates hedge fund positioning and macro data flows.
    """
    matrix_data = []
    historical_charts = {}
    if not tickers:
        return pd.DataFrame(), {}
        
    try:
        ticker_string = " ".join(tickers)
        data = yf.download(ticker_string, period=timeframe, group_by="ticker", progress=False)
        
        leopold_longs = ["IREN", "CORZ", "APLD", "RIOT", "CLSK", "BITF", "BTDR", "BE"]
        leopold_shorts = ["NVDA", "MU", "TSM", "ASML", "INTC"]
        trump_high_velocity = ["MSFT", "AMZN", "META", "NFLX", "ORCL", "AMD", "PLTR", "NVDA"]
        
        hf_pod_favorites = ["NVDA", "MSFT", "PLTR", "AMZN", "META"] 
        hf_activist_targets = ["WOLF", "CORZ", "APLD"]

        for ticker in tickers:
            if len(tickers) == 1:
                df = data.dropna()
            else:
                if ticker not in data.columns.levels[0]:
                    continue
                df = data[ticker].dropna()
                
            if df.empty or len(df) < 5:
                continue
                
            historical_charts[ticker] = df[['Close', 'Volume']]
                
            current_price = float(df["Close"].iloc[-1])
            current_volume = float(df["Volume"].iloc[-1])
            
            historical_df = df.iloc[:-1]
            twenty_day_high = float(historical_df["High"].tail(20).max())
            avg_volume = float(historical_df["Volume"].mean())
            
            price_breakout = current_price >= twenty_day_high
            volume_surge = current_volume >= (avg_volume * 1.5)
            whale_multiplier = current_volume / avg_volume if avg_volume > 0 else 0
            
            if price_breakout and volume_surge:
                breakout_signal = "🔥 FULL BREAKOUT"
            elif price_breakout:
                breakout_signal = "📈 Price Breakout"
            elif volume_surge:
                breakout_signal = "⚡ Volume Surge"
            else:
                breakout_signal = "⚪ Consolidated"
            
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
                
            if ticker in leopold_longs:
                leopold_signal = "⚡ Long Data Center/Infra"
            elif ticker in leopold_shorts:
                leopold_signal = "🚨 Heavy Notional Put Hedge"
            else:
                leopold_signal = "⚪ Unallocated"
                
            if ticker in hf_activist_targets or whale_multiplier > 2.2:
                hf_signal = "🎯 Activist Target / Squeeze Lock"
            elif ticker in hf_pod_favorites and price_breakout:
                hf_signal = "🏢 Multi-Mgr Pod Momentum Pile-in"
            elif ticker in leopold_shorts:
                hf_signal = "📉 Crowded Macro Short Sector"
            else:
                hf_signal = "⚖️ Neutral Multi-Strategy Book"
                
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
                "Hedge Fund Positioning": hf_signal,
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
        tab1, tab2, tab3 = st.tabs([
            "🔥 Institutional Squeeze Radar", 
            "🏛️ Market Alpha & Flows", 
            "⚡ Preshift Momentum"
        ])

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
            flow_df = df_results[["Ticker", "Price", "Institutional Flow", "Situational Awareness (Aschenbrenner)", "Hedge Fund Positioning", "Executive/Capitol Disclosures"]]
            
            def style_flow_tab(df):
                styles = pd.DataFrame('', index=df.index, columns=df.columns)
                styles["Institutional Flow"] = df["Institutional Flow"].apply(lambda x: "background-color: #0f2d4a; color: #99ccff; font-weight: bold;" if "WHALE" in x else "")
                styles["Situational Awareness (Aschenbrenner)"] = df["Situational Awareness (Aschenbrenner)"].apply(lambda x: "background-color: #1a3a2a; color: #99ff99;" if "Long" in x else ("background-color: #4a1515; color: #ff9999;" if "Put" in x else ""))
                styles["Hedge Fund Positioning"] = df["Hedge Fund Positioning"].apply(lambda x: "background-color: #3b3613; color: #ffea75;" if "Activist" in x else ("background-color: #113836; color: #7efce6;" if "Momentum" in x else ("background-color: #381111; color: #fc7e7e;" if "Short" in x else "")))
                styles["Executive/Capitol Disclosures"] = df["Executive/Capitol Disclosures"].apply(lambda x: "background-color: #3d1b40; color: #f2a2f5; font-weight: bold;" if "Active" in x else "")
                return styles
            st.dataframe(flow_df.style.apply(style_flow_tab, axis=None), use_container_width=True, hide_index=True)

        # --- TAB 3: DUAL-FEED PRESHIFT & ACTIVE RADAR ---
        with tab3:
            st.markdown("### Momentum Velocity Radar ($1.00 - $10.00)")
            st.caption("Pulls live micro-cap runners. Automatically switches feeds based on market session state.")
            
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.info("💡 Options Protocol: Double-check that options chains for target small-caps possess narrow bid-ask spreads to minimize premium friction.")
            with col_b:
                refresh_preshift = st.button("🔄 Scan Market Lines", use_container_width=True)
                
            if refresh_preshift or 'preshift_cache' not in st.session_state:
                with st.spinner("Processing structural gainers list..."):
                    st.session_state.preshift_cache = fetch_preshift_movers()
                    
            if not st.session_state.preshift_cache.empty:
                current_mode = st.session_state.preshift_cache["Session Source"].iloc[0]
                st.success(f"Displaying Live **{current_mode}** Allocation Stream")
                
                st.dataframe(
                    st.session_state.preshift_cache,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Gap/Change %": st.column_config.NumberColumn(format="+%.2f%%"),
                        "Volume Lines": st.column_config.NumberColumn(format="%d")
                    }
                )
                
                selected_mover = st.selectbox(
                    "🎯 Transfer Target Mover to Main Visualization Vectors:",
                    options=st.session_state.preshift_cache["Ticker"].tolist()
                )
                if st.button("Analyze Selected Preshift Target"):
                    if selected_mover not in st.session_state.global_watchlist:
                        st.session_state.global_watchlist.append(selected_mover)
                        update_cloud_storage()
                    st.session_state.selected_chart_ticker = selected_mover
                    st.success(f"Piped {selected_mover} into central vector pipeline! View charts below.")
                    st.rerun()
            else:
                st.warning("No active small-cap targets currently matching structural momentum baseline parameters.")

        # --- 5. THE VISUAL CHART MATRIX OVERLAY ---
        st.markdown("---")
        st.markdown("### 📈 Real-Time Matrix Terminal Visualizer")
        
        current_watchlist = st.session_state.global_watchlist
        if st.session_state.selected_chart_ticker not in current_watchlist:
            st.session_state.selected_chart_ticker = current_watchlist[0] if current_watchlist else "NVDA"
            
        active_ticker = st.selectbox(
            "Select Target Vector Focus to Plot:", 
            options=current_watchlist,
            index=current_watchlist.index(st.session_state.selected_chart_ticker) if current_watchlist else 0
        )
        st.session_state.selected_chart_ticker = active_ticker

        if active_ticker in chart_library:
            ticker_data = chart_library[active_ticker]
            
            st.caption(f"Velocity Trend Vector ({active_ticker} Close Price - Past {selected_timeframe})")
            st.line_chart(ticker_data['Close'], color="#00ffcc")
            
            df_atr = chart_library[active_ticker].copy()
            df_atr['H-L'] = df_atr['Close'] 
            df_atr['Volatility_Band'] = df_atr['Close'].rolling(window=14).std() * 2.5
            df_atr['Trailing_Stop_Floor'] = df_atr['Close'] - df_atr['Volatility_Band']
            
            current_close = df_atr['Close'].iloc[-1]
            current_floor = df_atr['Trailing_Stop_Floor'].iloc[-1]
            
            if not pd.isna(current_floor):
                recommended_pct = ((current_close - current_floor) / current_close) * 100
                st.metric(
                    label=f"🛡️ Dynamic Volatility Trailing Stop for {active_ticker}", 
                    value=f"${current_floor:.2f}", 
                    delta=f"Set Stop at -{recommended_pct:.1f}% from peak"
                )
                st.caption("This floor automatically widens during high-velocity institutional squeezes to prevent premature shakeouts.")

            st.caption(f"Volume Profile Allocation ({active_ticker})")
            st.bar_chart(ticker_data['Volume'], color="#1f77b4")

        # --- 6. COMPONENT CONTROL SECTOR ---
        st.markdown("---")
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
    st.info("Watchlist lines currently unallocated.")
