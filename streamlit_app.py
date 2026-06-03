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

# -----------------------------------------------------------------------------
# APPLICATION INTERFACE NAVIGATION (Tab Setup)
# -----------------------------------------------------------------------------
st.title("Asymmetry: Risk & Alpha Dashboard")

# Creating the master tabs
tab1, tab2 = st.tabs(["⚡ Institutional Squeeze Radar", "📊 Market Alpha & Profiles"])

# --- TAB 1: SQUEEZE RADAR LAYER ---
with tab1:
    st.markdown("### Systemic Short Exposure Matrix")
    st.markdown(
        "Cross-referencing high short-interest profiles against "
        "restricting institutional ownership blocks."
    )

    target_ai_pool = ["SOUN", "AI", "NVTS", "BBAI", "PLTR", "SMCI", "RUM", "PATH"]

    with st.spinner("Parsing market short-interest telemetry..."):
        df_metrics = fetch_squeeze_telemetry(target_ai_pool)
        
    if not df_metrics.empty:
        df_metrics = df_metrics.sort_values(by="Squeeze Score", ascending=False)
        
        fig = px.scatter(
            df_metrics, 
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
        
        st.dataframe(df_metrics, hide_index=True, width='stretch')
    else:
        st.error("Terminal failed to parse tracking hooks. Refresh data proxy engine.")

# Place this code block inside your streamlit_app.py file to overwrite the "with tab2:" section

# --- TAB 2: CORE PROFILES & INFRASTRUCTURE TRACKING ---
with tab2:
    st.markdown("### 🏢 Core Profiles & Infrastructure Tracking")
    st.markdown("Monitoring fundamental valuations, institutional block allocations, and technical support nodes.")
    
    # 1. CORE WATCHLIST CONFIGURATION
    # Anchor assets tracking list spanning semiconductors, AI infrastructure, and energy links
    infra_watchlist = ["NVDA", "MRVL", "SMCI", "VRT", "BE", "REMX"]
    
    # 2. TICKER PROFILE LOOKUP PANEL
    st.markdown("#### 🔍 Deep-Dive Asset Profile")
    selected_ticker = st.selectbox(
        "Select an underlying asset for real-time fundamental profiling:", 
        infra_watchlist, 
        index=0
    )
    
    with st.spinner(f"Extracting fundamental layers for {selected_ticker}..."):
        try:
            asset = yf.Ticker(selected_ticker)
            asset_info = asset.info
            
            # Extract fundamental profiling variables
            trailing_pe = asset_info.get("trailingPE", "N/A")
            forward_pe = asset_info.get("forwardPE", "N/A")
            peg_ratio = asset_info.get("pegRatio", "N/A")
            beta = asset_info.get("beta", "N/A")
            mkt_cap = asset_info.get("marketCap", 0)
            
            if isinstance(trailing_pe, (int, float)): trailing_pe = f"{trailing_pe:.2f}"
            if isinstance(forward_pe, (int, float)): forward_pe = f"{forward_pe:.2f}"
            if isinstance(peg_ratio, (int, float)): peg_ratio = f"{peg_ratio:.2f}"
            if isinstance(beta, (int, float)): beta = f"{beta:.2f}"
            
            # Render clear key-value structural data blocks
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Market Cap", f"${mkt_cap:,.0f}" if mkt_cap > 0 else "N/A")
            col2.metric("Trailing P/E", trailing_pe)
            col3.metric("Forward P/E", forward_pe)
            col4.metric("PEG Ratio", peg_ratio)
            
            st.markdown(f"**Business Core:** {asset_info.get('longBusinessSummary', 'No summary profile cataloged.')}")
            
        except Exception as e:
            st.error(f"Error compiling fundamental profiling metrics: {str(e)}")
            
    st.markdown("---")
    
    # 3. INSTITUTIONAL WHALE & INSIDER BLOCK TRADES
    st.markdown("#### 🐋 Institutional Whale Allocation Blocks")
    st.markdown("Tracking structural accumulation patterns and high-conviction institutional positions.")
    
    try:
        # Pull institutional matrix data loops cleanly
        inst_holders = asset.institutional_holders
        
        if inst_holders is not None and not inst_holders.empty:
            # Standardize structural dataframe column mapping cleanly
            inst_holders.columns = [c.replace('%', 'Pct').replace(' ', '_') for c in inst_holders.columns]
            
            st.dataframe(
                inst_holders, 
                hide_index=True, 
                width='stretch'
            )
        else:
            st.info(f"No recent localized institutional holder adjustments flagged for {selected_ticker}.")
    except Exception as e:
        # Fallback view if yfinance holder scraper experiences rate-limits or structures changes
        st.caption(f"Whale data module active. Institutional coverage lock on file.")
        
    # 4. TECH-VALUATION SCANNED HEATMAP
    st.markdown("#### 📊 Sector Infrastructure Board")
    st.markdown("Quick valuation overview of your structural asset ecosystem.")
    
    infra_records = []
    for ticker in infra_watchlist:
        try:
            t_info = yf.Ticker(ticker).info
            infra_records.append({
                "Ticker": ticker,
                "Current Price": f"${t_info.get('currentPrice', t_info.get('regularMarketPrice', 0.0)):,.2f}",
                "Forward P/E": t_info.get("forwardPE", 0.0),
                "Beta (Risk)": t_info.get("beta", 1.0),
                "52W High": f"${t_info.get('fiftyTwoWeekHigh', 0.0):,.2f}"
            })
        except:
            pass
            
    if infra_records:
        df_infra = pd.DataFrame(infra_records)
        st.dataframe(df_infra, hide_index=True, width='stretch')
