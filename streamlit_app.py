import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sec_api import InsiderTradingApi

# Initialize the SEC API Client (Requires your sec-api.io key)
# Make sure to add your SEC_API_KEY to your Streamlit secrets (.streamlit/secrets.toml)
SEC_API_KEY = st.secrets["SEC_API_KEY"]
insider_api = InsiderTradingApi(api_key=SEC_API_KEY)

def fetch_high_conviction_insiders(days_back=14):
    """
    Queries the SEC EDGAR database for Form 4 filings, bypassing automated plans
    and focusing strictly on open-market, cold-hard-cash purchases.
    """
    # Calculate date lookback
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    # CRITICAL ALPHA FILTERS:
    # 1. documentType: Form 4 (Changes in beneficial ownership)
    # 2. transactionCode: "P" (Strictly Open Market or Private Purchases)
    # 3. isRule10b51: false (Ignores automatic, pre-scheduled robotic trades)
    lucene_query = (
        f"documentType:\"4\" AND "
        f"nonDerivativeTransactions.transactionCode:\"P\" AND "
        f"nonDerivativeTransactions.isRule10b51:\"false\" AND "
        f"filingDate:[{start_date} TO *]"
    )
    
    try:
        # Request data from SEC endpoint
        response = insider_api.get_transactions({"query": lucene_query, "size": 50})
        transactions = response.get("transactions", [])
        
        parsed_trades = []
        for trade in transactions:
            # Safely extract top-level metadata
            ticker = trade.get("issuer", {}).get("tradingSymbol", "N/A")
            company_name = trade.get("issuer", {}).get("name", "N/A")
            insider_name = trade.get("reportingOwner", {}).get("name", "N/A")
            
            # Extract specific roles (Flagging high-level executive authority)
            is_director = trade.get("reportingOwner", {}).get("isDirector", False)
            is_officer = trade.get("reportingOwner", {}).get("isOfficer", False)
            is_ceo = "CEO" in str(trade.get("reportingOwner", {}).get("officerTitle", "")).upper()
            
            role = "Other"
            if is_ceo: role = "CEO"
            elif is_officer: role = "Officer"
            elif is_director: role = "Director"

            # Parse individual line items inside the transaction array
            for item in trade.get("nonDerivativeTransactions", []):
                # Ensure we only pull the actual cash buy rows within the form
                if item.get("transactionCode") == "P" and item.get("isRule10b51") == "false":
                    shares = float(item.get("transactionShares", 0) or 0)
                    price = float(item.get("transactionPricePerShare", 0) or 0)
                    total_value = shares * price
                    shares_owned_after = float(item.get("sharesOwnedFollowingTransaction", 0) or 0)
                    
                    # Calculate how aggressively they expanded their existing position
                    position_increase_pct = 0
                    if (shares_owned_after - shares) > 0:
                        position_increase_pct = (shares / (shares_owned_after - shares)) * 100

                    # Filter out tiny tracking trades (Only show transactions over $10,000)
                    if total_value >= 10000:
                        parsed_trades.append({
                            "Date": trade.get("filingDate"),
                            "Ticker": ticker,
                            "Company": company_name,
                            "Insider": insider_name,
                            "Role": role,
                            "Shares Bought": f"{shares:,.0f}",
                            "Avg Price": f"${price:,.2f}",
                            "Total Outlay": total_value, # Kept as float for sorting
                            "Position Jump": f"+{position_increase_pct:.1f}%" if shares_owned_after else "New Pos"
                        })
                        
        df = pd.DataFrame(parsed_trades)
        if not df.empty:
            return df.sort_values(by="Total Outlay", ascending=False).reset_index(drop=True)
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"Data Pipeline Error: {e}")
        return pd.DataFrame()

def detect_insider_clusters(df, window_days=14):
    """
    Finds the 'Asymmetry'. Identifies stocks where multiple distinct 
    insiders are buying within the same timeframe.
    """
    if df.empty:
        return []
    
    # Group by Ticker and count distinct insiders
    cluster_counts = df.groupby("Ticker")["Insider"].nunique()
    # High Conviction Trigger: 2 or more distinct buyers inside the window
    high_conviction_tickers = cluster_counts[cluster_counts >= 2].index.tolist()
    
    return high_conviction_tickers

# ──────────────────────────────────────────────────────────
# STREAMLIT UI INTEGRATION
# ──────────────────────────────────────────────────────────
st.title("Asymmetry Engine // C-Suite Direct Activity")
st.markdown("---")

with st.spinner("Scraping direct SEC EDGAR Form 4 feeds..."):
    raw_insider_data = fetch_high_conviction_insiders(days_back=14)

if not raw_insider_data.empty:
    # 1. High Conviction Alerts (The Clustered Buys)
    clusters = detect_insider_clusters(raw_insider_data)
    if clusters:
        st.subheader("🚨 TRIPLE CONVICTION INSIDER CLUSTERS DETECTED")
        for ticker in clusters:
            st.error(f"**{ticker}**: Multiple executive minds are committing cash here simultaneously inside the 14-day window.")
            
    st.markdown("---")
    
    # 2. Main Live Feed Data Display
    st.subheader("Live Open-Market Cash Outlays (Cleaned Feed)")
    
    # Format the monetary value for cleaner display without ruining the sorting properties earlier
    display_df = raw_insider_data.copy()
    display_df["Total Outlay"] = display_df["Total Outlay"].apply(lambda x: f"${x:,.2f}")
    
    st.dataframe(display_df, use_container_width=True)
else:
    st.info("No manual, open-market cash purchases over $10k detected in the trailing 14 days.")
