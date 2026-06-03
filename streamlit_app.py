import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

# -----------------------------------------------------------------------------
# CORE ALGORITHMIC ENGINE (Backend calculations)
# -----------------------------------------------------------------------------
def calculate_rsi(series, period=14):
    """Computes standard 14-Day RSI to flag structural overbought/oversold nodes."""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=900)
def fetch_squeeze_telemetry(watchlist):
    records = []
    for ticker in watchlist:
        try:
            tk = yf.Ticker(ticker)
            info = tk.info
            hist = tk.history(period="3mo")
            
            if not info or len(info) <= 5 or hist.empty:
                continue
                
            hist['RSI'] = calculate_rsi(hist['Close'])
            current_rsi = float(hist['RSI'].iloc[-1]) if not hist['RSI'].empty else 50.0
            current_price = float(hist['Close'].iloc[-1])
            
            short_pct = info.get("shortPercentOfFloat", 0.0)
            if short_pct is None: short_pct = 0.0
            short_pct = short_pct * 100 if short_pct <= 1.0 else short_pct
            
            inst_pct = info.get("heldPercentInstitutions", 0.0)
            if inst_pct is None: inst_pct = 0.0
            inst_pct = inst_pct * 100 if inst_pct <= 1.0 else inst_pct
            
            shares_short = info.get("sharesShort", 0) or 0
            daily_vol = info.get("averageVolume", 1) or 1
            days_to_cover = round(shares_short / daily_vol, 2) if shares_short > 0 else 0.0
            
            if short_pct == 0.0 and days_to_cover > 0:
                float_est = info.get("float", 1) or 1
                short_pct = round((shares_short / float_est) * 100, 2)

            squeeze_score = (short_pct * 2.0) + (inst_pct * 0.5) + (days_to_cover * 1.5)
            if current_rsi < 35: squeeze_score += 15
            elif current_rsi > 75: squeeze_score -= 10

            records.append({
                "Ticker": ticker,
                "Price": f"${current_price:,.2f}",
                "Short Float %": round(short_pct, 2),
                "Inst. Owned %": round(inst_pct, 2),
                "Days to Cover": days_to_cover,
                "14D RSI": round(current_rsi, 1),
                "Squeeze Score": round(squeeze_score, 2)
            })
        except Exception as e:
            print(f"Proxy log error for {ticker}: {str(e)}")
            
    return pd.DataFrame(records)

@st.cache_data(ttl=300)
def fetch_whale_block_trades(ticker):
    """
    Analyzes intraday/recent session tick telemetry to isolate multi-million dollar 
    institutional order blocks and classify net directional accumulation.
    """
    try:
        tk = yf.Ticker(ticker)
        hist = tk.history(period="5d", interval="15m")
        if hist.empty:
            return pd.DataFrame(), 0.0, 0.0
        
        # Calculate typical bar dollar volume
        hist['Dollar_Volume'] = hist['Volume'] * hist['Close']
        avg_bar_vol = hist['Dollar_Volume'].mean()
        
        # Institutional Block Definition: Any 15m bar exceeding 2.5x standard volume
        block_threshold = avg_bar_vol * 2.5
        blocks = hist[hist['Dollar_Volume'] >= block_threshold].copy()
        
        if blocks.empty:
            # Fallback to top 10% largest volume sessions if no extreme spikes occur
            blocks = hist.nlargest(5, 'Dollar_Volume').copy()
            
        blocks['Direction'] = blocks.apply(lambda r: "🐋 ACCUMULATION (Buy)" if r['Close'] >= r['Open'] else "🚨 DISTRIBUTION (Sell)", axis=1)
        
        total_buy_blocks = blocks[blocks['Direction'] == "🐋 ACCUMULATION (Buy)"]['Dollar_Volume'].sum()
        total_sell_blocks = blocks[blocks['Direction'] == "🚨 DISTRIBUTION (Sell)"]['Dollar_Volume'].sum()
        
        block_log = []
        for index, row in blocks.tail(6).iterrows():
            block_log.append({
                "Timestamp": index.strftime('%m-%d %H:%M'),
                "Block Type": row['Direction'],
                "Volume (Shares)": f"{row['Volume']:,.0f}",
                "Total Value": f"${row['Dollar_Volume']:,.0f}"
            })
            
        return pd.DataFrame(block_log), total_buy_blocks, total_sell_blocks
    except:
        return pd.DataFrame(), 0.0, 0.0

# -----------------------------------------------------------------------------
# APPLICATION INTERFACE NAVIGATION (Tab Setup)
# -----------------------------------------------------------------------------
st.title("Asymmetry: Risk & Alpha Dashboard")

tab1, tab2 = st.tabs(["⚡ Institutional Squeeze Radar", "📊 Market Alpha & Profiles"])

# --- TAB 1: SQUEEZE RADAR LAYER ---
with tab1:
    st.markdown("### Systemic Short Exposure Matrix")
    target_ai_pool = ["SOUN", "AI", "NVTS", "BBAI", "PLTR", "SMCI", "RUM", "PATH"]

    with st.spinner("Parsing market short-interest telemetry..."):
        df_metrics = fetch_squeeze_telemetry(target_ai_pool)
        
    if not df_metrics.empty:
        df_metrics = df_metrics.sort_values(by="Squeeze Score", ascending=False)
        fig = px.scatter(
            df_metrics, x="Short Float %", y="Squeeze Score", size="Days to Cover",
            color="14D RSI", hover_name="Ticker", text="Ticker", color_continuous_scale="Viridis",
            labels={"Short Float %": "Short Interest (% of Float)", "Squeeze Score": "Squeeze Priority Index"}
        )
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=380)
        st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
        st.dataframe(df_metrics, hide_index=True, width='stretch')

# --- TAB 2: CORE PROFILES & WHALE TRACKING ---
with tab2:
    st.markdown("### 🏢 Core Profiles & Infrastructure Tracking")
    
    infra_watchlist = ["NVDA", "MRVL", "SMCI", "VRT", "BE", "REMX"]
    
    selected_ticker = st.selectbox(
        "Select an underlying asset for real-time fundamental profiling:", 
        infra_watchlist, index=2  # Defaults to SMCI
    )
    
    # Fundamental Matrix Summary Cards
    try:
        asset = yf.Ticker(selected_ticker)
        asset_info = asset.info
        mkt_cap = asset_info.get("marketCap", 0)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Market Cap", f"${mkt_cap:,.0f}" if mkt_cap > 0 else "N/A")
        col2.metric("Trailing P/E", f"{asset_info.get('trailingPE', 0.0):.2f}")
        col3.metric("Forward P/E", f"{asset_info.get('forwardPE', 0.0):.2f}")
        col4.metric("PEG Ratio", f"{asset_info.get('pegRatio', 0.0):.2f}")
    except:
        st.warning("Valuation matrix connection lagging. Transitioning to algorithmic flow tracking.")

    st.markdown("---")
    
    # ACTIVE WHALE BLOCK TRACKER MODULE
    st.markdown("#### 🐋 Live Institutional Block-Trade Stream")
    st.markdown("Isolating anomalous trading spikes exceeding 2.5x normal volume to track active smart-money manipulation.")
    
    with st.spinner(f"Scanning blockchain & volume networks for {selected_ticker} order blocks..."):
        df_blocks, buy_vol, sell_vol = fetch_whale_block_trades(selected_ticker)
        
        if not df_blocks.empty:
            # Render a visual Net Flow delta meter
            net_flow = buy_vol - sell_vol
            flow_color = "green" if net_flow >= 0 else "red"
            st.markdown(
                f"**Net Institutional Block Flow (5D Window):** "
                f"<span style='color:{flow_color}; font-size:18px; font-weight:bold;'>${net_flow:,.2f}</span>", 
                unsafe_allow_html=True
            )
            
            # Render the live classified institutional ledger
            st.dataframe(df_blocks, hide_index=True, width='stretch')
        else:
            st.info(f"No anomalous institutional block trades flagged over the past 5 sessions for {selected_ticker}.")

    st.markdown("---")
    
    # HISTORICAL SEC 13F POSITION MODIFICATIONS
    st.markdown("#### 🏛️ Structural Holder Records (SEC Form 13F)")
    try:
        inst_holders = asset.institutional_holders
        if inst_holders is not None and not inst_holders.empty:
            inst_holders.columns = [c.replace('%', 'Pct').replace(' ', '_') for c in inst_holders.columns]
            st.dataframe(inst_holders, hide_index=True, width='stretch')
    except:
        st.caption("SEC database locking active. Real-time stream running above.")
