# --- ENHANCED DYNAMIC HELPERS IN DATA_STORE.PY ---

# Extended sector lookup for automatic categorization
SECTOR_MAP = {
    "NVDA": "Semiconductors / AI Infrastructure",
    "INTC": "Semiconductors / Manufacturing",
    "MRVL": "Semiconductors / Data Infrastructure",
    "STX": "Hardware / Data Storage",
    "FIX": "Industrial Infrastructure / Construction",
    "POWL": "Industrial Infrastructure / Power Grid",
    "ALB": "Specialty Chemicals / Mining",
    "COPX": "Commodities / Copper Miners ETF",
    "ANFGF": "Commodities / Lithium Mining",
    "PLTR": "Defense Tech / AI Analytics",
    "BE": "Clean Energy / Utilities",
    "DELL": "Tech Hardware / Enterprise Infrastructure",
    "AVGO": "Semiconductors / AI Connectivity",
    "AMD": "Semiconductors / Compute Engines",
    "GS": "Financials / Investment Banking",
    "JPM": "Financials / Banking",
    "LITE": "Optical Tech / Telecom",
    "SMCI": "Hardware / AI Server Liquid Cooling",
    "VRT": "Industrial Infrastructure / Data Center Liquid Cooling",
    "CEG": "Utilities / Data Center Nuclear Power",
    "MU": "Semiconductors / High-Bandwidth Memory",
    "ANET": "Tech Hardware / AI Networking"
}

def get_sector(ticker):
    """Smart helper to dynamically categorize any typed-in ticker"""
    tk = ticker.upper().strip()
    if tk in SECTOR_MAP:
        return SECTOR_MAP[tk]
    
    # Smart string matching guesses if the ticker isn't in our dictionary
    if any(x in tk for x in ["ETF", "Fund", "X"]): 
        return "Macro / Index Fund Asset"
    if any(x in tk for x in ["AI", "TECH", "DIGI"]): 
        return "Emerging Tech / Digital Architecture"
    
    # Universal professional fallback description
    return "High-Conviction Tracking Target"


# --- UPDATE INSIDER RANDOMIZER LOOP INSIDER DATA STORE ---
# Replace the old loop inside def get_insider_data_raw(watchlist=None): with this:

    if watchlist:
        existing_tickers = {item["Ticker"] for item in base_data}
        
        # Pools of realistic names and roles to break up the "Systemic Accumulation" repetition
        mock_insiders = ["Vanguard Trust", "Blackstone Group", "Sovereign Asset Mgmt", "Altimeter Alpha", "Matrix Capital", "Apex Holdings"]
        mock_execs = ["CEO / President", "Chief Financial Officer", "Director", "10% Beneficial Owner", "Executive VP"]
        
        for ticker in watchlist:
            ticker = ticker.upper().strip()
            if ticker not in existing_tickers:
                is_buy = random.choice([True, False])
                val = random.randint(150000, 950000)
                
                base_data.append({
                    "Filing Date": datetime.now().strftime("%Y-%m-%d"),
                    "Ticker": ticker,
                    "Insider": random.choice(mock_insiders), # Varied names
                    "Role": random.choice(mock_execs),       # Varied roles
                    "Type": "🟢 Purchase" if is_buy else "🔴 Sale",
                    "Value ($)": val if is_buy else -val
                })
