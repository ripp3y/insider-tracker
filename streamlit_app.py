import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sec_api import QueryApi
import yfinance as yf

# ──────────────────────────────────────────────────────────
# CONFIGURATION & GLOBAL SETUP
# ──────────────────────────────────────────────────────────
st.set_page_config(page_title="Asymmetry Dashboard", layout="wide")

MASTER_WATCHLIST = [
    "FIX", "VRT", "CIEN", "SMCI", "BE", 
    "NVDA", "MRVL", "TSM", "UMC", "POWL", "AGX",
    "STX", "COPX", "ANFGF", "ALB", "REMX", "DVN"
]

# Load SEC API Key from Streamlit Secrets securely
SEC_API_KEY = st.secrets.get("SEC_API_KEY", "")

# ──────────────────────────────────────────────────────────
# SIDEBAR CONTROLS
# ──────────────────────────────────────────────────────────
st.sidebar.title("🦅 Asymmetry Control Panel")

if not SEC_API_KEY:
    SEC_API_KEY = st.sidebar.text_input("Enter SEC-API.io Key:", type="password")
else:
    st.sidebar.success("🔑 SEC Connection Authenticated.")

if not SEC_API_KEY:
    st.warning("⚠️ Please provide your SEC-API.io key in the sidebar or Cloud Secrets to run the terminal components.")
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
# TAB 2: STRUCTURAL UPTREND RADAR (VOLUME SURGE METRICS)
# ──────────────────────────────────────────────────────────
with tab_radar:
    st.subheader("Master Matrix Trend Architecture")
    st.markdown("Tracks multi-timeframe structure alongside RSI overbought indicators and relative volume surge velocity.")
    
    @st.cache_data(ttl=600)
    def calculate_trend_metrics_hardened(ticker_list):
        screened_data = []
        
        tickers_string = " ".join(ticker_list)
        try:
            batch_data = yf.download(tickers_string, period="1y", group_by="ticker", threads=False, progress=False)
        except Exception:
            batch_data = pd.DataFrame()
            
        for ticker in ticker_list:
            df = pd.DataFrame()
            
            if not batch_data.empty and ticker in batch_data.columns.levels[0]:
                df = batch_data[ticker].dropna()
                
            if df.empty or len(df) < 200:
                try:
                    asset = yf.Ticker(ticker)
                    df = asset.history(period="1y").dropna()
                except Exception:
                    continue

            if df.empty or len(df) < 200:
                continue

            try:
                close_col = 'Close' if 'Close' in df.columns else '4. close'
                vol_col = 'Volume' if 'Volume' in df.columns else '5. volume'
                
                close_series = df[close_col].astype(float)
                vol_series = df[vol_col].astype(float)
                
                current_price = float(close_series.iloc[-1])
                sma_50 = float(close_series.rolling(window=50).mean().iloc[-1])
                sma_200 = float(close_series.rolling(window=200).mean().iloc[-1])
                
                # UPDATED: Calculate relative volume surge over a 20-day baseline
                current_volume = float(vol_series.iloc[-1])
                avg_volume_20d = float(vol_series.rolling(window=20).mean().iloc[-1])
                
                volume_surge_pct = 0.0
                if avg_volume_20d > 0:
                    volume_surge_pct = ((current_volume - avg_volume_20d) / avg_volume_20d) * 100
                
                # Compute Relative Strength Index (RSI 14)
                delta = close_series.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / (loss + 1e-9)
                rsi = float(100 - (100 / (1 + rs)).iloc[-1])
                
                if current_price > sma_50 and sma_50 > sma_200:
                    status = "🔥 Strong Uptrend"
                elif current_price > sma_200 and current_price <= sma_50:
                    status = "⏳ Support Test"
                else:
                    status = "⚠️ Structural Breakdown"
                    
                dist_to_50 = ((current_price - sma_50) / sma_50) * 100
                dist_to_200 = ((current_price - sma_200) / sma_200) * 100
                
                screened_data.append({
                    "Ticker": ticker,
                    "Price": f"${current_price:.2f}",
                    "Structure": status,
                    "RSI (14)": f"{rsi:.1f}",
                    "Vol Surge (20D MA)": f"{volume_surge_pct:+.1f}%",  # Replaced raw column with formatted percentage deviation
                    "SMA 50 Support": f"${sma_50:.2f}",
                    "Dist to SMA 50": f"{dist_to_50:+.1f}%",
                    "SMA 200 Floor": f"${sma_200:.2f}",
                    "Dist to SMA 200": f"{dist_to_200:+.1f}%",
                    "raw_sort": dist_to_50
                })
            except Exception:
                pass
                
        return pd.DataFrame(screened_data)

    if st.button("🔄 Execute Hardened Matrix Scan"):
        with st.spinner("Compiling multi-timeframe structural trends..."):
            radar_df = calculate_trend_metrics_hardened(MASTER_WATCHLIST)

            if st.button("🔄 Execute Hardened Matrix Scan"):
        with st.spinner("Compiling multi-timeframe structural trends..."):
            radar_df = calculate_trend_metrics_hardened(MASTER_WATCHLIST)

        if not radar_df.empty:
            # 1. Properly sort and strip out the raw temporary sorting key
            radar_df = radar_df.sort_values(by="raw_sort", ascending=False).drop(columns=["raw_sort"]).reset_index(drop=True)
            
            # 2. Build the visual matrix with styling and hide the index cleanly
            st.dataframe(
                radar_df.style.map(
                    lambda val: "background-color: rgba(40, 167, 69, 0.15);" if "🔥" in str(val)
                    else ("background-color: rgba(255, 193, 7, 0.15);" if "⏳" in str(val)
                    else ("background-color: rgba(220, 53, 69, 0.15);" if "⚠️" in str(val) else "")),
                    subset=["Structure"]
                ),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("The market data servers are heavily congested. Wait a few moments and run the scan again.")
