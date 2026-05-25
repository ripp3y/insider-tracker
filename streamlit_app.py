import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sec_api import InsiderTradingApi

# ──────────────────────────────────────────────────────────
# CONFIGURATION & API KEY HANDLING
# ──────────────────────────────────────────────────────────
st.set_page_config(page_title="Asymmetry Insider Engine", layout="wide")

# Attempt to load the key from Streamlit's cloud secrets first
SEC_API_KEY = st.secrets.get("SEC_API_KEY", "")

# Sidebar configuration
st.sidebar.title("Configuration")

# If the key isn't found in secrets, let you paste it right on the screen
if not SEC_API_KEY:
    SEC_API_KEY = st.sidebar.text_input(
        "Enter SEC-API.io Key:", 
        type="password",
        help="Get a free api key from sec-api.io to power this dashboard."
    )
    if not SEC_API_KEY:
        st.warning("⚠️ Please configure your 'SEC_API_KEY' in your Streamlit Cloud Secrets or enter it in the sidebar to load the data feed.")
        st.stop()
else:
    st.sidebar.success("🔑 SEC API Key loaded from Cloud Secrets.")

# Lookback filter adjustment directly in the UI
days_back = st.sidebar.slider("Lookback Window (Days)", min_value=3, max_value=30, value=14)

# Initialize the API client safely
insider_api = InsiderTradingApi(api_key=SEC_API_KEY)

# ──────────────────────────────────────────────────────────
# DATA PIPELINE FUNCTIONS
# ──────────────────────────────────────────────────────────
def fetch_high_conviction_insiders(days_to_search=14):
    """
    Queries SEC EDGAR for Form 4 open-market cash transactions.
    Deletes the automated 10b51 noise automatically.
    """
    start_date = (datetime.now() - timedelta(days=days_to_search)).strftime('%Y-%m-%d')
    
    # Raw lucene query targeting strict cash buys
    lucene_query = (
        f"documentType:\"4\" AND "
        f"nonDerivativeTransactions.transactionCode:\"P\" AND "
        f"nonDerivativeTransactions.isRule10b51:\"false\" AND "
        f"filingDate:[{start_date} TO *]"
    )
    
    try:
        response = insider_api.get_transactions({"query": lucene_query, "size": 50})
        transactions = response.get("transactions", [])
        
        parsed_trades = []
        for trade in transactions:
            ticker = trade.get("issuer", {}).get("tradingSymbol", "N/A")
            company_name = trade.get("issuer", {}).get("name", "N/A")
            insider_name = trade.get("reportingOwner", {}).get("name", "N/A")
            
            # Identify internal corporate roles
            is_director = trade.get("reportingOwner", {}).get("isDirector", False)
            is_officer = trade.get("reportingOwner", {}).get("isOfficer", False)
            officer_title = trade.get("reportingOwner", {}).get("officerTitle", "")
            
            role = "Other"
            if "CEO" in str(officer_title).upper() or "CHIEF EXECUTIVE" in str(officer_title).upper():
                role = "CEO"
            elif is_officer:
                role = f"Officer ({officer_title})" if officer_title else "Officer"
            elif is_director:
                role = "Director"

            for item in trade.get("nonDerivativeTransactions", []):
                if item.get("transactionCode") == "P" and item.get("isRule10b51") == "false":
                    shares = float(item.get("transactionShares", 0) or 0)
                    price = float(item.get("transactionPricePerShare", 0) or 0)
                    total_value = shares * price
                    shares_owned_after = float(item.get("sharesOwnedFollowingTransaction", 0) or 0)
                    
                    # Calculate depth of position increase
                    position_increase_pct = 0
                    if (shares_owned_after - shares) > 0:
                        position_increase_pct = (shares / (shares_owned_after - shares)) * 100

                    # Focus strictly on meaningful allocations (>$10,000 out of pocket)
                    if total_value >= 10000:
                        parsed_trades.append({
                            "Filing Date": trade.get("filingDate"),
                            "Ticker": ticker,
                            "Company Name": company_name,
                            "Insider Trader": insider_name,
                            "Corporate Role": role,
                            "Shares Copped": f"{shares:,.0f}",
                            "Price Paid": f"${price:,.2f}",
                            "Total Outlay": total_value, # Numeric for sorting
                            "Position Increase": f"+{position_increase_pct:.1f}%" if shares_owned_after else "New Stake"
                        })
                        
        df = pd.DataFrame(parsed_trades)
        if not df.empty:
            return df.sort_values(by="Total Outlay", ascending=False).reset_index(drop=True)
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"SEC Pipeline Query Error: {e}")
        return pd.DataFrame()

def detect_insider_clusters(df):
    """
    Identifies high-asymmetry tickers where multiple independent corporate
    insiders are spending cash simultaneously.
    """
    if df.empty:
        return []
    cluster_counts = df.groupby("Ticker")["Insider Trader"].nunique()
    return cluster_counts[cluster_counts >= 2].index.tolist()

# ──────────────────────────────────────────────────────────
# MAIN ENGINE DASHBOARD DISPLAY
# ──────────────────────────────────────────────────────────
st.title("🦅 Asymmetry Engine // Live Corporate Insiders")
st.markdown("Scraping direct SEC EDGAR Form 4 feeds for real-time open-market cash buys. Pre-scheduled robotic trades are filtered out.")
st.markdown("---")

with st.spinner(f"Extracting live cash flows from past {days_back} days..."):
    raw_insider_data = fetch_high_conviction_insiders(days_to_search=days_back)

if not raw_insider_data.empty:
    # 1. Trigger System (The Multi-Insider Cluster Alerts)
    clusters = detect_insider_clusters(raw_insider_data)
    if clusters:
        st.error("### 🚨 MULTI-EXECUTIVE BUYING CLUSTERS")
        cols = st.columns(len(clusters) if len(clusters) < 4 else 4)
        for idx, ticker in enumerate(clusters):
            with cols[idx % 4]:
                st.metric(
                    label=f"High Conviction Target: {ticker}", 
                    value="CLUSTER ALERT", 
                    delta="Multiple Insiders Buying"
                )
        st.markdown("---")
            
    # 2. Main Live Feed Display Table
    st.subheader(f"Raw Insider Cash Commitments (Past {days_back} Days)")
    
    # Format the monetary amount cleanly for printing without ruining the data sort order
    display_df = raw_insider_data.copy()
    display_df["Total Outlay"] = display_df["Total Outlay"].apply(lambda x: f"${x:,.2f}")
    
    st.dataframe(display_df, use_container_width=True)
else:
    st.info(f"No direct open-market cash deployments greater than $10,000 detected in the trailing {days_back} days.")
