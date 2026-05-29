import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
from sec_api import QueryApi
from alpha_vantage.timeseries import TimeSeries

# ──────────────────────────────────────────────────────────
# CONFIGURATION & GLOBAL SETUP
# ──────────────────────────────────────────────────────────
st.set_page_config(page_title="Asymmetry Dashboard", layout="wide")

MASTER_WATCHLIST = [
    "FIX", "VRT", "CIEN", "SMCI", "BE", 
    "NVDA", "MRVL", "TSM", "UMC", "POWL", "AGX",
    "STX", "COPX", "ANFGF", "ALB", "REMX", "DVN"
]

# Load API Keys from Streamlit Secrets securely
SEC_API_KEY = st.secrets.get("SEC_API_KEY", "")
AV_API_KEY = st.secrets.get("AV_API_KEY", "")

# ──────────────────────────────────────────────────────────
# SIDEBAR CONTROLS
# ──────────────────────────────────────────────────────────
st.sidebar.title("🦅 Asymmetry Control Panel")

if not SEC_API_KEY:
    SEC_API_KEY = st.sidebar.text_input("Enter SEC-API.io Key:", type="password")
else:
    st.sidebar.success("🔑 SEC Connection Authenticated.")

if not AV_API_KEY:
    AV_API_KEY = st.sidebar.text_input(
        "Enter Alpha Vantage Key:", 
        type="password", 
        help="Get a free key at alphavantage.co to bypass Yahoo rate limits."
    )
else:
    st.sidebar.success("🔑 Market Data Pipeline Secure.")

av_tier = st.sidebar.selectbox("Alpha Vantage Key Tier", ["Free Tier (Compact)", "Premium (Uncapped)"])

if not SEC_API_KEY or not AV_API_KEY:
    st.warning("⚠️ Please provide both API keys in the sidebar or Cloud Secrets to run the terminal components.")
    st.stop()

lookback_days = st.sidebar.slider("Insider Tracking Window (Days)", min_value=3, max_value=30, value=14)

# ──────────────────────────────────────────────────────────
# TABS LAYOUT
# ──────────────────────────────────────────────────────────
tab_insider, tab_radar = st.tabs(["🕵️‍♂️ Live C-Suite Insiders", "📈 Structural Uptrend Radar"])

query_api = QueryApi(api_key=SEC_API_KEY)

# ──────────────────────────────────────────────────────────
# TAB 1: INSIDER TRADING LOGIC
# ──────────────────────────────────────────────────────────
with tab_insider:
    st.subheader("Real-Time Corporate Insider Outlays")
    st.markdown("Scraping direct SEC EDGAR Form 4 streams. Automated robotic 10b51 plans are completely omitted.")
    
    @st.cache_data(ttl=300)
    def fetch_high_conviction_insiders(days_to_search):
        start_date = (datetime.now() - timedelta(days=days_to_search)).strftime('%Y-%m-%d')
        
        lucene_query = (
            f"formType:\"4\" AND "
            f"filedAt:[{start_date} TO *] AND "
            f"transactions.transactionCode:\"P\" AND "
            f"transactions.isRule10b51:\"false\""
        )
        
        payload = {
            "query": { "query_string": { "query": lucene_query } },
            "from": "0",
            "size": "50",
            "sort": [{ "filedAt": { "order": "desc" } }]
        }
        
        try:
            response = query_api.get_filings(payload)
            filings = response.get("filings", [])
            parsed_trades = []
            
            for filing in filings:
                issuer = filing.get("issuer", {})
                if not issuer: continue
                    
                ticker = issuer.get("tradingSymbol", "N/A")
                company_name = issuer.get("name", "N/A")
                reporting_owner = filing.get("reportingOwner", {})
                insider_name = reporting_owner.get("name", "N/A") if reporting_owner else "N/A"
                
                role = "Other"
                if reporting_owner:
                    is_director = reporting_owner.get("isDirector", False)
                    is_officer = reporting_owner.get("isOfficer", False)
                    officer_title = reporting_owner.get("officerTitle", "")
                    if "CEO" in str(officer_title).upper(): role = "CEO"
                    elif is_officer: role = f"Officer ({officer_title})" if officer_title else "Officer"
                    elif is_director: role = "Director"

                for tx in filing.get("nonDerivativeTransactions", []):
                    if tx.get("transactionCode") == "P" and str(tx.get("isRule10b51")).lower() != "true":
                        shares = float(tx.get("transactionShares", 0) or 0)
                        price = float(tx.get("transactionPricePerShare", 0) or 0)
                        total_value = shares * price
                        shares_owned_after = float(tx.get("sharesOwnedFollowingTransaction", 0) or 0)
                        
                        position_increase_pct = 0
                        if (shares_owned_after - shares) > 0:
                            position_increase_pct = (shares / (shares_owned_after - shares)) * 100

                        if total_value >= 10000:
                            parsed_trades.append({
                                "Filing Date": filing.get("filedAt")[:10] if filing.get("filedAt") else "N/A",
                                "Ticker": ticker,
                                "Company Name": company_name,
                                "Insider Trader": insider_name,
                                "Role": role,
                                "Shares Bought": f"{shares:,.0f}",
                                "Price Paid": f"${price:,.2f}",
                                "Total Outlay": total_value,
                                "Position Jump": f"+{position_increase_pct:.1f}%" if shares_owned_after else "New Stake"
                            })
                            
            df = pd.DataFrame(parsed_trades)
            return df.sort_values(by="Total Outlay", ascending=False).reset_index(drop=True) if not df.empty else pd.DataFrame()
        except Exception as e:
            st.error(f"SEC Query Engine Error: {e}")
            return pd.DataFrame()

    with st.spinner("Extracting SEC filings..."):
        insider_df = fetch_high_conviction_insiders(lookback_days)

    if not insider_df.empty:
        cluster_counts = insider_df.groupby("Ticker")["Insider Trader"].nunique()
        clusters = cluster_counts[cluster_counts >= 2].index.tolist()
        if clusters:
            st.error(f"### 🚨 MULTI-INSIDER CLUSTERS SPOTTED: {', '.join(clusters)}")
        
        display_insider = insider_df.copy()
        display_insider["Total Outlay"] = display_insider["Total Outlay"].apply(lambda x: f"${x:,.2f}")
        st.dataframe(display_insider, use_container_width=True)
    else:
        st.info("No manual cash purchases detected over $10k in this timeframe.")

# ──────────────────────────────────────────────────────────
# TAB 2: STRUCTURAL UPTREND RADAR (COMPACT MODE OPTIMIZED)
# ──────────────────────────────────────────────────────────
with tab_radar:
    st.subheader("Master Matrix Trend Architecture")
    st.markdown("Scans key moving averages via optimized compact pipeline to run within Free Tier restrictions.")
    
    @st.cache_data(ttl=3600)
    def calculate_trend_metrics_av(ticker_list, api_key, tier):
        screened_data = []
        ts = TimeSeries(key=api_key, output_format='pandas')
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Initial burst safeguard pause
        time.sleep(2)
        
        for idx, ticker in enumerate(ticker_list):
            try:
                status_text.text(f"Streaming market data for: {ticker} ({idx+1}/{len(ticker_list)})")
                
                # FIXED: Removed outputsize='full' to remain compatible with Free tier
                if tier == "Premium (Uncapped)":
                    df, meta = ts.get_daily(symbol=ticker, outputsize='full')
                else:
                    df, meta = ts.get_daily(symbol=ticker, outputsize='compact')
                    
                df = df.sort_index(ascending=True)

                if df.empty or len(df) < 50: 
                    st.warning(f"Skipped {ticker}: Insufficient historical data.")
                    continue

                close_series = df['4. close'].astype(float)
                current_price = float(close_series.iloc[-1])
                
                # Calculating moving averages within the 100-day available limit
                sma_20 = float(close_series.rolling(window=20).mean().iloc[-1])
                sma_50 = float(close_series.rolling(window=50).mean().iloc[-1])
                
                delta = close_series.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / (loss + 1e-9)
                rsi = float(100 - (100 / (1 + rs)).iloc[-1])
                
                if current_price > sma_20 and sma_20 > sma_50:
                    status = "🔥 Strong Uptrend"
                elif current_price > sma_50 and current_price <= sma_20:
                    status = "⏳ Support Test"
                else:
                    status = "⚠️ Structural Breakdown"
                    
                dist_to_20 = ((current_price - sma_20) / sma_20) * 100
                dist_to_50 = ((current_price - sma_50) / sma_50) * 100
                
                screened_data.append({
                    "Ticker": ticker,
                    "Price": round(current_price, 2),
                    "Structure": status,
                    "RSI (14)": round(rsi, 1),
                    "SMA 20 Level": round(sma_20, 2),
                    "Dist to SMA 20": f"{dist_to_20:+.1f}%",
                    "SMA 50 Support": round(sma_50, 2),
                    "Dist to SMA 50": f"{dist_to_50:+.1f}%",
                    "raw_sort": dist_to_50
                })
                
                progress_bar.progress((idx + 1) / len(ticker_list))
                
                if tier == "Free Tier (Compact)" and idx < len(ticker_list) - 1:
                    for remaining in range(14, 0, -1):
                        status_text.text(f"Cooling down API to avoid rate limits... ({remaining}s remaining before next pull)")
                        time.sleep(1)
                        
            except Exception as e:
                # Catching strings returned by Alpha Vantage API messages
                error_msg = str(e)
                if "premium" in error_msg.lower():
                    st.error(f"🛑 Alpha Vantage Tier Conflict: Free keys require 'Free Tier (Compact)' selected in sidebar.")
                    break
                else:
                    st.warning(f"Skipped {ticker}: {error_msg}")
                
        status_text.empty()
        progress_bar.empty()
        return pd.DataFrame(screened_data)

    if st.button("🔄 Execute Matrix Scan"):
        with st.spinner("Analyzing structural trends..."):
            radar_df = calculate_trend_metrics_av(MASTER_WATCHLIST, AV_API_KEY, av_tier)

        if not radar_df.empty:
            radar_df = radar_df.sort_values(by="raw_sort", ascending=False).drop(columns=["raw_sort"]).reset_index(drop=True)
            
            st.dataframe(
                radar_df.style.map(
                    lambda val: "background-color: rgba(40, 167, 69, 0.15);" if "🔥" in str(val)
                    else ("background-color: rgba(255, 193, 7, 0.15);" if "⏳" in str(val)
                    else ("background-color: rgba(220, 53, 69, 0.15);" if "⚠️" in str(val) else "")),
                    subset=["Structure"]
                ),
                use_container_width=True
            )
        else:
            st.info("No matrix data processed. Adjust settings or verify limits.")
