import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. CORE ALGORITHMIC ENGINE (Backend Calculations)
# -----------------------------------------------------------------------------
def calculate_rsi(series, period=14):
    """Computes standard 14-Day RSI to flag structural overbought/oversold nodes."""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / (loss + 1e-9)  # Prevent divide-by-zero
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=900)
def fetch_squeeze_telemetry(watchlist):
    """Parses short interest data and flags short squeeze risk models."""
    if not watchlist:
        return pd.DataFrame()
        
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
            
            # Standardize short interest variables
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

            # Algorithmic Squeeze Priority Weighting
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
    """Analyzes 15-minute bars to isolate institutional blocks."""
    try:
        tk = yf.Ticker(ticker)
        hist = tk.history(period="5d", interval="15m")
        if hist.empty:
            return pd.DataFrame(), 0.0, 0.0
        
        hist['Dollar_Volume'] = hist['Volume'] * hist['Close']
        avg_bar_vol = hist['Dollar_Volume'].mean()
        block_threshold = avg_bar_vol * 2.5
        blocks = hist[hist['Dollar_Volume'] >= block_threshold].copy()
        
        if blocks.empty:
            blocks = hist.nlargest(5, 'Dollar_Volume').copy()
            
        blocks['Direction'] = blocks.apply(
            lambda r: "🐋 ACCUMULATION (Buy)" if r['Close'] >= r['Open'] else "🚨 DISTRIBUTION (Sell)", 
            axis=1
        )
        
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
# 2. DYNAMIC SIDEBAR WATCHLIST MANAGER
# -----------------------------------------------------------------------------
st.sidebar.title("🎛️ Watchlist Control Room")

# Initial seed list combining your core tech and squeeze metrics
default_watch = ["SOUN", "AI", "NVTS", "BBAI", "PLTR", "SMCI", "RUM", "PATH", "NVDA", "MRVL", "VRT", "BE"]

if "global_watchlist" not in st.session_state:
    st.session_state.global_watchlist = default_watch

# Add New Ticker Input
new_ticker = st.sidebar.text_input("Add Ticker (e.g. AMD, TSLA):").upper().strip()
if st.sidebar.button("➕ Add to Watchlist") and new_ticker:
    if new_ticker not in st.session_state.global_watchlist:
        st.session_state.global_watchlist.append(new_ticker)
        st.rerun()

# Delete Ticker Selector
ticker_to_remove = st.sidebar.selectbox("Select ticker to remove:", [""] + st.session_state.global_watchlist)
if st.sidebar.button("🗑️ Delete from Watchlist") and ticker_to_remove:
    st.session_state.global_watchlist.remove(ticker_to_remove)
    st.rerun()

# Display Current Raw Watchlist Pool
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Active Pool Count:** `{len(st.session_state.global_watchlist)}` tickers")
st.sidebar.caption(", ".join(st.session_state.global_watchlist))


# -----------------------------------------------------------------------------
# 3. APPLICATION INTERFACE NAVIGATION (Tab Setup)
# -----------------------------------------------------------------------------
st.title("Asymmetry: Risk & Alpha Dashboard")

tab1, tab2 = st.tabs(["⚡ Institutional Squeeze Radar", "📊 Market Alpha & Profiles"])

# --- TAB 1: AUTOMATED SQUEEZE RADAR (TOP 8 NOISE FILTER) ---
with tab1:
    st.markdown("### Systemic Short Exposure Matrix")
    st.markdown("Algorithmic filter parsing your custom watchlist pool and presenting **only the top 8 assets** with acute short exposure risk matrices.")

    if not st.session_state.global_watchlist:
        st.info("Your watchlist pool is empty. Add tickers via the sidebar panel to activate scanning pipelines.")
    else:
        with st.spinner("Parsing market short-interest telemetry..."):
            df_metrics = fetch_squeeze_telemetry(st.session_state.global_watchlist)
            
        if not df_metrics.empty:
            # NOISE FILTER: Sort by highest score and grab exactly the top 8 candidates
            df_filtered = df_metrics.sort_values(by="Squeeze Score", ascending=False).head(8)
            
            fig = px.scatter(
                df_filtered, 
                x="Short Float %", 
                y="Squeeze Score", 
                size="Days to Cover",
                color="14D RSI",
                hover_name="Ticker",
                text="Ticker",
                color_continuous_scale="Viridis",
                labels={"Short Float %": "Short Interest (% of Float)", "Squeeze Score": "Squeeze Priority Index"}
            )
            fig.update_traces(textposition="top center", marker=dict(line=dict(width=1, color='DarkSlateGrey')))
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=30, b=10),
                height=380
            )
            st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
            
            # Show full metrics for just these top 8 candidates
            st.dataframe(df_filtered, hide_index=True, width='stretch')
        else:
            st.error("Terminal failed to parse tracking hooks. Verify network proxies.")


# --- TAB 2: CORE PROFILES, WHALES, & SECTOR INFRASTRUCTURE ---
with tab2:
    st.markdown("### 🏢 Core Profiles & Infrastructure Tracking")
    st.markdown("Monitoring fundamental valuations, institutional block allocations, and technical support nodes.")
    
    if not st.session_state.global_watchlist:
        st.info("Your watchlist pool is empty. Add tickers via the sidebar panel to select asset profiles.")
    else:
        selected_ticker = st.selectbox(
            "Select an underlying asset for real-time fundamental profiling:", 
            st.session_state.global_watchlist, 
            index=0
        )
        
        # Fundamental Matrix Key Cards
        try:
            asset = yf.Ticker(selected_ticker)
            asset_info = asset.info
            mkt_cap = asset_info.get("marketCap", 0)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Market Cap", f"${mkt_cap:,.0f}" if mkt_cap > 0 else "N/A")
            col2.metric("Trailing P/E", f"{asset_info.get('trailingPE', 0.0):.2f}" if asset_info.get('trailingPE') else "N/A")
            col3.metric("Forward P/E", f"{asset_info.get('forwardPE', 0.0):.2f}" if asset_info.get('forwardPE') else "N/A")
            col4.metric("PEG Ratio", f"{asset_info.get('pegRatio', 0.0):.2f}" if asset_info.get('pegRatio') else "N/A")
            
            st.markdown(f"**Business Core:** {asset_info.get('longBusinessSummary', 'No profile cataloged.')}")
        except:
            st.warning("Valuation matrix connection lagging. Transitioning to active live telemetry streams.")

        st.markdown("---")
        
        # 2. Active Whale Block Tracker Module
        st.markdown("#### 🐋 Live Institutional Block-Trade Stream")
        with st.spinner(f"Scanning volume networks for {selected_ticker} order blocks..."):
            df_blocks, buy_vol, sell_vol = fetch_whale_block_trades(selected_ticker)
            
            if not df_blocks.empty:
                net_flow = buy_vol - sell_vol
                flow_color = "green" if net_flow >= 0 else "red"
                st.markdown(
                    f"**Net Institutional Block Flow (5D Window):** "
                    f"<span style='color:{flow_color}; font-size:18px; font-weight:bold;'>${net_flow:,.2f}</span>", 
                    unsafe_allow_html=True
                )
                st.dataframe(df_blocks, hide_index=True, width='stretch')
            else:
                st.info(f"No anomalous institutional block trades flagged over the past 5 sessions for {selected_ticker}.")

        st.markdown("---")
        
        # 3. Sector Infrastructure Board & Heatmap
        st.markdown("#### 📊 Sector Infrastructure Broadboard")
        st.markdown("Cross-comparing real-time risk profiles and pullbacks for all items in your global watchlist.")
        
        infra_records = []
        with st.spinner("Compiling full sector matrix data..."):
            for ticker in st.session_state.global_watchlist:
                try:
                    t_ticker = yf.Ticker(ticker)
                    t_info = t_ticker.info
                    t_hist = t_ticker.history(period="1mo")
                    
                    current_p = t_info.get('currentPrice') or t_info.get('regularMarketPrice') or (t_hist['Close'].iloc[-1] if not t_hist.empty else 0.0)
                    fifty_two_w_high = t_info.get('fiftyTwoWeekHigh', 1e-9) or 1e-9
                    
                    pct_off_high = ((fifty_two_w_high - current_p) / fifty_two_w_high) * 100
                    if pct_off_high < 0: pct_off_high = 0.0
                    
                    if not t_hist.empty:
                        t_hist['RSI'] = calculate_rsi(t_hist['Close'])
                        current_rsi_val = t_hist['RSI'].iloc[-1]
                    else:
                        current_rsi_val = 50.0

                    infra_records.append({
                        "Ticker": ticker,
                        "Price": f"${current_p:,.2f}",
                        "Forward P/E": round(t_info.get("forwardPE", 0.0), 2) if t_info.get("forwardPE") else "N/A",
                        "Beta (Risk Factor)": round(t_info.get("beta", 1.0), 2) if t_info.get("beta") else 1.0,
                        "14D RSI": round(current_rsi_val, 1),
                        "Discount from 52W High %": round(pct_off_high, 2)
                    })
                except Exception as e:
                    print(f"Watchlist row error for {ticker}: {str(e)}")
                    
        if infra_records:
            df_infra = pd.DataFrame(infra_records)
            
            fig_infra = px.bar(
                df_infra,
                x="Ticker",
                y="Discount from 52W High %",
                color="14D RSI",
                text_auto=".1f",
                color_continuous_scale="rdylbu_r",
                labels={"Discount from 52W High %": "Pullback Depth (% Off Peak)", "14D RSI": "Momentum (RSI)"}
            )
            fig_infra.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=20, b=10),
                height=300
            )
            st.plotly_chart(fig_infra, width='stretch', config={'displayModeBar': False})
            st.dataframe(df_infra, hide_index=True, width='stretch')

        st.markdown("---")
        
        # 4. Historical SEC 13F Position Records
        st.markdown("#### 🏛 McKay / Corporate Structural Holder Records (SEC Form 13F)")
        try:
            inst_holders = asset.institutional_holders
            if inst_holders is not None and not inst_holders.empty:
                inst_holders.columns = [c.replace('%', 'Pct').replace(' ', '_') for c in inst_holders.columns]
                st.dataframe(inst_holders, hide_index=True, width='stretch')
        except:
            st.caption("SEC quarterly reporting archive database locked. Real-time ticker pipelines streaming above.")
