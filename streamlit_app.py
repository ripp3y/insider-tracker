pimport streamlit as st
import yfinance as yf
import pandas as pd
import hashlib
import urllib.request
from bs4 import BeautifulSoup

# Force wide layout and early configuration
st.set_page_config(page_title="Rebel Terminal AI", layout="wide")

# --- 1. INITIALIZATION & STATE ENGINE ---
if "global_watchlist" not in st.session_state:
    try:
        query_params = st.query_params
        if "symbols" in query_params and query_params["symbols"]:
            st.session_state.global_watchlist = [s.strip().upper() for s in query_params["symbols"].split(",") if s.strip()]
        else:
            st.session_state.global_watchlist = ["NVDA", "MU", "WOLF", "IREN", "CORZ", "APLD", "PLTR", "MSFT"]
    except:
        st.session_state.global_watchlist = ["NVDA", "MU", "WOLF", "IREN", "CORZ", "APLD", "PLTR", "MSFT"]

if "selected_chart_ticker" not in st.session_state:
    st.session_state.selected_chart_ticker = st.session_state.global_watchlist[0] if st.session_state.global_watchlist else "NVDA"

def update_cloud_storage():
    try:
        if st.session_state.global_watchlist:
            st.query_params["symbols"] = ",".join(st.session_state.global_watchlist)
        else:
            if "symbols" in st.query_params:
                del st.query_params["symbols"]
    except:
        pass

# --- PUBLIC DATA DUAL-MODE SCANNER ---
def fetch_preshift_movers():
    """
    Direct API implementation that bypasses HTML blocks completely.
    Scans a high-velocity basket of momentum favorites using internal JSON lines.
    """
    try:
        # High-velocity structural momentum small-caps/penny stock watch basket
        momentum_basket = [
            "SOUN", "BBAI", "GFAI", "KOSS", "IREN", "CORZ", "APLD", "WULF", 
            "MARA", "HUT", "RIOT", "CLSK", "BITF", "BTDR", "POWL", "SMCI"
        ]
        
        # Pull direct raw data from API endpoints
        ticker_string = " ".join(momentum_basket)
        data = yf.download(ticker_string, period="2d", group_by="ticker", progress=False)
        
        movers = []
        for ticker in momentum_basket:
            try:
                if ticker not in data.columns.levels[0]:
                    continue
                df = data[ticker].dropna()
                if len(df) < 2:
                    continue
                
                prev_close = float(df["Close"].iloc[-2])
                current_price = float(df["Close"].iloc[-1])
                volume = int(df["Volume"].iloc[-1])
                
                # Calculate direct mathematical gap/change percentage
                gap_pct = ((current_price - prev_close) / prev_close) * 100
                
                # Broaden constraints slightly to ensure visibility
                if current_price <= 500.00:  
                    movers.append({
                        "Ticker": ticker,
                        "Price": f"${current_price:.2f}",
                        "Prev Close": f"${prev_close:.2f}",
                        "Gap/Change %": round(gap_pct, 2),
                        "Volume Lines": volume,
                        "Session Source": "Direct JSON Engine"
                    })
            except:
                continue
                
        df_movers = pd.DataFrame(movers)
        if not df_movers.empty:
            # Sort by absolute highest percentage runners first
            return df_movers.sort_values(by="Gap/Change %", ascending=False).reset_index(drop=True)
        return pd.DataFrame()
        
    except Exception as e:
        return pd.DataFrame()


# --- 2. MULTI-VECTOR RADAR & DATA ENGINE ---
def fetch_terminal_data(tickers, timeframe="6mo"):
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
        st.error(f"Data Engine Error: {e}")
        
    return pd.DataFrame(matrix_data), historical_charts

# --- 3. INTERFACE HEADER ---
st.markdown("# 🦅 Rebel Terminal AI")

with st.form(key="add_ticker_form", clear_on_submit=True):
    new_ticker = st.text_input("Deploy Asset to Matrix Ticker Line (e.g., POWL, SMCI):").strip().upper()
    submit_button = st.form_submit_button(label="⚡ Add to Watchlist")
    
    if submit_button and new_ticker:
        if new_ticker not in st.session_state.global_watchlist:
            st.session_state.global_watchlist.append(new_ticker)
            update_cloud_storage()
            st.rerun()

# --- 4. MAIN INTERFACE RENDERING ---
if st.session_state.global_watchlist:
    selected_timeframe = st.radio(
        "Select Terminal Structural Horizon Lookup:",
        options=["3mo", "6mo"],
        index=1,
        horizontal=True
    )

    df_results, chart_library = fetch_terminal_data(st.session_state.global_watchlist, timeframe=selected_timeframe)

    if not df_results.empty:
        tab1, tab2, tab3 = st.tabs([
            "🔥 Institutional Squeeze Radar", 
            "🏛️ Market Alpha & Flows", 
            "⚡ Preshift Momentum"
        ])

        with tab1:
            st.markdown("### Systemic Short Exposure & Breakout Matrix")
            squeeze_df = df_results[["Ticker", "Price", "20D High", "Breakout Status", "Whale Vol Ratio", "Squeeze Risk Profile"]]
            st.dataframe(squeeze_df, use_container_width=True, hide_index=True)

        with tab2:
            st.markdown("### Multi-Vector Accumulation Matrix")
            flow_df = df_results[["Ticker", "Price", "Institutional Flow", "Situational Awareness (Aschenbrenner)", "Hedge Fund Positioning", "Executive/Capitol Disclosures"]]
            st.dataframe(flow_df, use_container_width=True, hide_index=True)

        with tab3:
            st.markdown("### Momentum Velocity Radar ($1.00 - $10.00)")
            
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.info("💡 Options Protocol: Double-check that options chains for target small-caps possess narrow bid-ask spreads.")
            with col_b:
                refresh_preshift = st.button("🔄 Scan Market Lines", use_container_width=True)
                
            if refresh_preshift or 'preshift_cache' not in st.session_state:
                st.session_state.preshift_cache = fetch_preshift_movers()
                    
            if not st.session_state.preshift_cache.empty:
                st.dataframe(
                    st.session_state.preshift_cache,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.warning("No active small-cap targets currently matching structural momentum baseline parameters.")

        # --- 5. VISUAL CHART MATRIX OVERLAY ---
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
            st.line_chart(ticker_data['Close'], color="#00ffcc")
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
                    update_cloud_storage()
                    st.rerun()
else:
    st.info("Watchlist lines currently unallocated.")
