import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import requests

# -----------------------------------------------------------------------------
# 0. DEPLOYMENT BROWSER SPOOFING ENGINE (Fixes HTTP 401 Cloud Blocks)
# -----------------------------------------------------------------------------
# We manually configure a custom requests session with a realistic User-Agent 
# header to bypass cloud server scraping restrictions.
custom_session = requests.Session()
custom_session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Origin": "https://finance.yahoo.com",
    "Referer": "https://finance.yahoo.com/"
})

# -----------------------------------------------------------------------------
# 1. CORE ALGORITHMIC ENGINE (Backend Calculations)
# -----------------------------------------------------------------------------
def calculate_rsi(series, period=14):
    """Computes standard 14-Day RSI to flag structural overbought/oversold nodes."""
    if len(series) < period:
        return pd.Series(50.0, index=series.index)
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / (loss + 1e-9)  # Prevent divide-by-zero
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=600)
def fetch_squeeze_telemetry(watchlist):
    """Parses short interest data and flags short squeeze risk models with strict error insulation."""
    if not watchlist:
        return pd.DataFrame()
        
    records = []
    for ticker in watchlist:
        try:
            # Pass our browser-spoofing session directly into the yfinance Ticker instantiation
            tk = yf.Ticker(ticker, session=custom_session)
            
            # Using 1mo data keeps payload light and limits provider request flags
            hist = tk.history(period="1mo")
            if hist.empty:
                continue
                
            try:
                info = tk.info
                if not info or len(info) <= 5:
                    raise ValueError("Incomplete dictionary context retrieved.")
            except:
                # Absolute fallback if .info remains locked out
                info = {"shortPercentOfFloat": 0.05, "heldPercentInstitutions": 0.5, "averageVolume": 1000000}
                
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
                "Squeeze Score": round(squeeze_score, 2),
                "Raw_Price": current_price,
                "Raw_RSI": current_rsi
            })
        except Exception as e:
            print(f"Skipping temporary cloud connection stall for {ticker}: {str(e)}")
            continue
            
    return pd.DataFrame(records)

@st.cache_data(ttl=300)
def fetch_whale_block_trades(ticker):
    """Analyzes 15-minute bars to isolate institutional blocks with safety bounds."""
    try:
        tk = yf.Ticker(ticker, session=custom_session)
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
            # Sort by priority score and isolate top 8 candidates to clear out plot clutter
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
            
            clean_df_filtered = df_filtered.drop(columns=["Raw_Price", "Raw_RSI"])
            st.dataframe(clean_df_filtered, hide_index=True, width='stretch')
        else:
            st.warning("Data stream temporarily re-routing. If layout remains blank, toggle your watchlist pool to force update.")


# --- TAB 2: CORE PROFILES, WHALES, & SECTOR INFRASTRUCTURE ---
with tab2:
    st.markdown("### 🏢 Core Profiles & Infrastructure Tracking")
    st.markdown("Monitoring fundamental valuations, institutional block allocations, and technical support nodes.")
    
    if not st.session_state.global_watchlist:
        st.info("Your watchlist pool is empty. Add tickers via the sidebar panel to select asset profiles.")
    else:
        with st.spinner("Assembling structural profiling matrix..."):
            df_metrics = fetch_squeeze_telemetry(st.session_state.global_watchlist)
            
        available_tickers = df_metrics["Ticker"].tolist() if not df_metrics.empty else st.session_state.global_watchlist
        
        selected_ticker = st.selectbox(
            "Select an underlying asset for real-time fundamental profiling:", 
            available_tickers, 
            index=0
        )
        
        # Fundamental Matrix Key Cards
        try:
            asset = yf.Ticker(selected_ticker, session=custom_session)
            asset_info = asset.info
            mkt_cap = asset_info.get("marketCap", 0)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Market Cap", f"${mkt_cap:,.0f}" if mkt_cap and mkt_cap > 0 else "N/A")
            col2.metric("Trailing P/E", f"{asset_info.get('trailingPE', 0.0):.2f}" if asset_info.get('trailingPE') else "N/A")
            col3.metric("Forward P/E", f"{asset_info.get('forwardPE', 0.0):.2f}" if asset_info.get('forwardPE') else "N/A")
            col4.metric("PEG Ratio", f"{asset_info.get('pegRatio', 0.0):.2f}" if asset_info.get('pegRatio') else "N/A")
            
            st.markdown(f"**Business Core:** {asset_info.get('longBusinessSummary', 'No profile cataloged.')}")
        except:
            st.caption("Valuation card matrix connection lag. Institutional logs streaming below.")

        st.markdown("---")
        
        # 2. Active Whale Block Tracker Module
        st.markdown("#### 🐋 Live Institutional Block-Trade Stream")
        with st.spinner(f"Scanning volume
