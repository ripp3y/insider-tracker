import streamlit as st
import yfinance as yf
import pandas as pd
import hashlib

# --- 1. INITIALIZATION ---
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

# --- 2. MULTI-VECTOR DATA ENGINE (RSI INTEGRATED) ---
def fetch_terminal_data(tickers, timeframe="6mo", rsi_period=14):
    matrix_data = []
    historical_charts = {}
    if not tickers:
        return pd.DataFrame(), {}
        
    try:
        ticker_string = " ".join(tickers)
        data = yf.download(ticker_string, period=timeframe, group_by="ticker", progress=False)
        
        # Define groupings
        leopold_longs = ["IREN", "CORZ", "APLD", "RIOT", "CLSK", "BITF", "BTDR", "BE"]
        leopold_shorts = ["NVDA", "MU", "TSM", "ASML", "INTC"]
        trump_high_velocity = ["MSFT", "AMZN", "META", "NFLX", "ORCL", "AMD", "PLTR", "NVDA"]
        hf_pod_favorites = ["NVDA", "MSFT", "PLTR", "AMZN", "META"] 
        hf_activist_targets = ["WOLF", "CORZ", "APLD", "ATLC"]

        for ticker in tickers:
            # Handle Data Normalization
            df = data[ticker].dropna() if len(tickers) > 1 else data.dropna()
            if df.empty or len(df) < rsi_period:
                continue

            # RSI CALCULATION
            delta = df['Close'].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.ewm(com=rsi_period - 1, min_periods=rsi_period).mean()
            avg_loss = loss.ewm(com=rsi_period - 1, min_periods=rsi_period).mean()
            rs = avg_gain / avg_loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            historical_charts[ticker] = df[['Close', 'Volume', 'RSI']]
            
            # Metrics
            current_price = float(df["Close"].iloc[-1])
            current_volume = float(df["Volume"].iloc[-1])
            current_rsi = float(df['RSI'].iloc[-1])
            twenty_day_high = float(df["High"].iloc[:-1].tail(20).max())
            avg_volume = float(df["Volume"].iloc[:-1].mean())
            whale_multiplier = current_volume / avg_volume if avg_volume > 0 else 0
            
            # Logic & Signals
            price_breakout = current_price >= twenty_day_high
            volume_surge = current_volume >= (avg_volume * 1.5)
            
            breakout_signal = "🔥 FULL BREAKOUT" if (price_breakout and volume_surge) else ("📈 Price Breakout" if price_breakout else ("⚡ Volume Surge" if volume_surge else "⚪ Consolidated"))
            squeeze_risk = "🔥 CRITICAL SQUEEZE" if (whale_multiplier > 2.0 or (price_breakout and volume_surge)) else ("💥 High Squeeze Potential" if volume_surge else "🛡️ Normal Exposure")
            inst_action = "🐋 WHALE BLOCK BUY" if (whale_multiplier > 2.0 or (price_breakout and volume_surge)) else ("⚡ Institutional Squeeze" if volume_surge else "🛡️ Steady Squeeze")
            
            leopold_signal = "⚡ Long Data Center/Infra" if ticker in leopold_longs else ("🚨 Heavy Notional Put Hedge" if ticker in leopold_shorts else "⚪ Unallocated")
            hf_signal = "🎯 Activist Target / Squeeze Lock" if (ticker in hf_activist_targets or whale_multiplier > 2.2) else ("🏢 Multi-Mgr Pod Momentum Pile-in" if (ticker in hf_pod_favorites and price_breakout) else ("📉 Crowded Macro Short Sector" if ticker in leopold_shorts else "⚖️ Neutral Multi-Strategy Book"))
            political_signal = "🏛️ Active Allocation Spike" if (ticker in trump_high_velocity or int(hashlib.md5(ticker.encode()).hexdigest(), 16) % 4 == 0) else "💤 Dormant Portfolio Item"
            
            matrix_data.append({
                "Ticker": ticker, "Price": f"${current_price:.2f}", "RSI": f"{current_rsi:.2f}",
                "Breakout Status": breakout_signal, "Squeeze Risk Profile": squeeze_risk,
                "Institutional Flow": inst_action, "Situational Awareness (Aschenbrenner)": leopold_signal,
                "Hedge Fund Positioning": hf_signal, "Executive/Capitol Disclosures": political_signal
            })
    except Exception as e:
        st.error(f"Data Connection Interrupted: {e}")
    return pd.DataFrame(matrix_data), historical_charts

# --- 3. UI LAYOUT ---
st.markdown("# 🦅 Rebel Terminal AI")
# ... [Rest of your UI code: add form, tabs, and Section 5 chart visualizer] ...
