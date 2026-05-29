import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from sec_api import InsiderTradingApi
from alpha_vantage.timeseries import TimeSeries

# ──────────────────────────────────────────────────────────
# CONFIGURATION & GLOBAL SETUP
# ──────────────────────────────────────────────────────────
st.set_page_config(page_title="Asymmetry Dashboard", layout="wide")

MASTER_WATCHLIST = [
    "FIX", "VRT", "CIEN", "SMCI", "BE", 
    "NVDA", "MRVL", "TSM", "UMC", "POWL", "AGX",
    "SNDK", "STX", "COPX", "ANFGF", "ALB", "REMX", "DVN"
]

# Load API Keys from Streamlit Secrets securely
SEC_API_KEY = st.secrets.get("SEC_API_KEY", "")
AV_API_KEY = st.secrets.get("AV_API_KEY", "")

# ──────────────────────────────────────────────────────────
# SIDEBAR CONTROLS
# ──────────────────────────────────────────────────────────
st.sidebar.title("🦅 Asymmetry Control Panel")

# SEC Key Validation
if not SEC_API_KEY:
    SEC_API_KEY = st.sidebar.text_input("Enter SEC-API.io Key:", type="password")
else:
    st.sidebar.success("🔑 SEC Connection Authenticated.")

# Alpha Vantage Key Validation (For Rate-Limit Immunity)
if not AV_API_KEY:
    AV_API_KEY = st.sidebar.text_input(
        "Enter Alpha Vantage Key:", 
        type="password", 
        help="Get a free key at alphavantage.co to bypass Yahoo rate limits."
    )
else:
    st.sidebar.success("🔑 Market Data Pipeline Secure.")

if not SEC_API_KEY or not AV_API_KEY:
    st.warning("⚠️ Please provide both API keys in the sidebar or Cloud Secrets to run the terminal components.")
    st.stop()

lookback_days = st.sidebar.slider("Insider Tracking Window (Days)", min_value=3, max_value=30, value=14)

# ──────────────────────────────────────────────────────────
# REBEL TABS LAYOUT
# ──────────────────────────────────────────────────────────
tab_insider, tab_radar = st.tabs(["🕵️‍♂️ Live C-Suite Insiders", "📈 Structural Uptrend Radar"])

insider_api = InsiderTradingApi(api_key=SEC_API_KEY)

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
            f"documentType:\"4\" AND "
            f"nonDerivativeTransactions.transactionCode:\"P\" AND "
            f"nonDerivativeTransactions.isRule10b51:\"false\" AND "
            f"filingDate:[{start_date} TO *]"
        )
        try:
            # CORRECTED: Using the universal '.get_data' API request wrapper method
            response = insider_api.get_data(lucene_query)
            transactions = response.get("transactions", []) if isinstance(response, dict) else []
            parsed_trades = []
            
            for trade in transactions:
                ticker = trade.get("issuer", {}).get("tradingSymbol", "N/A")
                company_name = trade.get("issuer", {}).get("name", "N/A")
                insider_name = trade.get("reportingOwner", {}).get("name", "N/A")
                
                is_director = trade.get("reportingOwner", {}).get("isDirector", False)
                is_officer = trade.get("reportingOwner", {}).get("isOfficer", False)
                officer_title = trade.get("reportingOwner", {}).get("officerTitle", "")
                
                role = "Other"
                if "CEO" in str(officer_title).upper(): role = "CEO"
                elif is_officer: role = f"Officer ({officer_title})" if officer_title else "Officer"
                elif is_director: role = "Director"

                for item in trade.get("nonDerivativeTransactions", []):
                    if item.get("transactionCode") == "P" and item.get("isRule10b51") == "false":
                        shares = float(item.get("transactionShares", 0) or 0)
                        price = float(item.get("transactionPricePerShare", 0) or 0)
                        total_value = shares * price
                        shares_owned_after = float(item.get("sharesOwnedFollowingTransaction", 0) or 0)
                        
                        position_increase_pct = 0
                        if (shares_owned_after - shares) > 0:
                            position_increase_pct = (shares / (shares_owned_after - shares)) * 100

                        if total_value >= 10000:
                            parsed_trades.append({
                                "Filing Date": trade.get("filingDate"),
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
            st.error(f"SEC API Error: {e}")
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
# TAB 2: STRUCTURAL UPTREND RADAR
# ──────────────────────────────────────────────────────────
with tab_radar:
    st.subheader("Master Matrix Trend Architecture")
    st.markdown("Scans key moving averages via Alpha Vantage pipeline to keep data moving smoothly without rate limits.")
    
    @st.cache_data(ttl=1800)
    def calculate_trend_metrics_av(ticker_list, api_key):
        screened_data = []
        ts = TimeSeries(key=api_key, output_format='pandas')
        
        for ticker in ticker_list:
            try:
                df, meta = ts.get_daily(symbol=ticker, outputsize='full')
                df.columns = [col.split('. ')[1].title() for col in df.columns]
                df = df.sort_index(ascending=True)

                if df.empty or len(df) < 200: 
                    continue

                close_series = df['Close']
                current_price = float(close_series.iloc[-1])
                sma_50 = float(close_series.rolling(window=50).mean().iloc[-1])
                sma_200 = float(close_series.rolling(window=200).mean().iloc[-1])
                
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
                    "Price": round(current_price, 2),
                    "Structure": status,
                    "RSI (14)": round(rsi, 1),
                    "SMA 50 Support": round(sma_50, 2),
                    "Dist to SMA 50": f"{dist_to_50:+.1f}%",
                    "SMA 200 Floor": round(sma_200, 2),
                    "Dist to SMA 200": f"{dist_to_200:+.1f}%",
                    "raw_sort": dist_to_50
                })
            except:
                pass
        return pd.DataFrame(screened_data)

    with st.spinner("Analyzing multi-timeframe trends via Alpha Vantage..."):
        radar_df = calculate_trend_metrics_av(MASTER_WATCHLIST, AV_API_KEY)

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
        st.info("Waiting for pipeline stream data to populate. Ensure Alpha Vantage API key is valid.")
