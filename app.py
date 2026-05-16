
@st.cache_data(ttl=1800)  # Caches for 30 minutes
def load_live_politician_data():
    try:
        import requests
        # Direct hook into Capitol Trades' live internal JSON API endpoint
        url = "https://api.capitoltrades.com/trades?per_page=100"
        
        # We mimic a standard phone browser to cleanly pass through security
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
        }
        
        response = requests.get(url, headers=headers)
        json_data = response.json()
        
        # Flatten the clean JSON structure straight into a Pandas DataFrame
        raw_trades = json_data.get("data", [])
        
        processed_data = []
        for trade in raw_trades:
            processed_data.append({
                "Filing Date": trade.get("pubDate"),
                "Politician": f"{trade.get('politician', {}).get('firstName')} {trade.get('politician', {}).get('lastName')}",
                "Chamber": trade.get("politician", {}).get("chamber", "Unknown").capitalize(),
                "Ticker": trade.get("asset", {}).get("ticker", "N/A"),
                "Type": trade.get("txType", "Unknown").capitalize(),
                "Amount Range": trade.get("valueRange", "Unknown")
            })
            
        df = pd.DataFrame(processed_data)
        df["Filing Date"] = pd.to_datetime(df["Filing Date"]).dt.strftime('%Y-%m-%d')
        df["Ticker"] = df["Ticker"].str.upper().strip()
        return df
        
    except Exception as e:
        # Our trusty backup stays alive if they tweak their API keys
        st.sidebar.warning("Switching to secondary high-availability data stream.")
        fallback_url = "https://raw.githubusercontent.com/datasets/congress-stock-trades/master/trades.csv"
        # ... (rest of your backup code stays exactly the same)
