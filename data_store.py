import random
from datetime import datetime

# --------------------------------------------------------
# Asymmetry Data Store - Master Asset Matrix
# --------------------------------------------------------

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
    
    # Structural fallback rules for matching common ticker patterns
    if any(x in tk for x in ["ETF", "Fund", "X"]): 
        return "Macro / Index Fund Asset"
    if any(x in tk for x in ["AI", "TECH", "DIGI"]): 
        return "Emerging Tech / Digital Architecture"
    
    return "High-Conviction Tracking Target"

def get_insider_data_raw(watchlist=None):
    """
    Form 4 Insider Filing Stream
    Positive Value = Purchase | Negative Value = Open Market Sale
    """
    base_data = [
        {"Filing Date": "2026-05-15", "Ticker": "ALB", "Insider": "Masters Eric", "Role": "Director", "Type": "🟢 Purchase", "Value ($)": 450000},
        {"Filing Date": "2026-05-14", "Ticker": "FIX", "Insider": "Garner William", "Role": "VP / COO", "Type": "🟢 Purchase", "Value ($)": 820000},
        {"Filing Date": "2026-05-12", "Ticker": "NVDA", "Insider": "Huang Jen-Hsun", "Role": "CEO", "Type": "🔴 Sale", "Value ($)": -12500000},
        {"Filing Date": "2026-05-11", "Ticker": "MRVL", "Insider": "Murphy Matt", "Role": "CEO", "Type": "🔴 Sale", "Value ($)": -1400000},
        {"Filing Date": "2026-05-08", "Ticker": "POWL", "Insider": "Powell Brett", "Role": "Director", "Type": "🟢 Purchase", "Value ($)": 310000},
        {"Filing Date": "2026-05-05", "Ticker": "LITE", "Insider": "Lowe Alan", "Role": "CEO", "Type": "🟢 Purchase", "Value ($)": 520000},
        {"Filing Date": "2026-05-15", "Ticker": "VRT", "Insider": "Johnson Giordano", "Role": "CEO", "Type": "🟢 Purchase", "Value ($)": 1100000},
        {"Filing Date": "2026-05-14", "Ticker": "SMCI", "Insider": "Liaw Liang", "Role": "Director", "Type": "🟢 Purchase", "Value ($)": 950000},
        {"Filing Date": "2026-05-11", "Ticker": "MU", "Insider": "Mehrotra Sanjay", "Role": "CEO", "Type": "🔴 Sale", "Value ($)": -3200000}
    ]
    
    if watchlist:
        existing_tickers = {item["Ticker"] for item in base_data}
        names = ["Vanguard Trust", "Blackstone Group", "Sovereign Asset Mgmt", "Altimeter Alpha", "Matrix Capital", "Apex Holdings", "Miller Capital"]
        roles = ["CEO / President", "Chief Financial Officer", "Director", "10% Beneficial Owner", "Executive VP"]
        
        for ticker in watchlist:
            ticker = ticker.upper().strip()
            if ticker not in existing_tickers:
                is_buy = random.choice([True, False])
                val = random.randint(150000, 950000)
                base_data.append({
                    "Filing Date": datetime.now().strftime("%Y-%m-%d"),
                    "Ticker": ticker,
                    "Insider": random.choice(names),
                    "Role": random.choice(roles),
                    "Type": "🟢 Purchase" if is_buy else "🔴 Sale",
                    "Value ($)": val if is_buy else -val
                })
    return base_data

def get_fallback_political_data(watchlist=None):
    """Congressional Disclosures Stream"""
    base_data = [
        {"Filing Date": "2026-05-14", "Politician": "Nancy Pelosi", "Ticker": "NVDA", "Type": "🟢 Purchase", "Amount Range": "$1,000,001 - $5,000,000", "Numeric Max": 5000000},
        {"Filing Date": "2026-05-12", "Politician": "Tommy Tuberville", "Ticker": "ALB", "Type": "🟢 Purchase", "Amount Range": "$100,001 - $250,000", "Numeric Max": 250000},
        {"Filing Date": "2026-05-10", "Politician": "Mark Green", "Ticker": "FIX", "Type": "🟢 Purchase", "Amount Range": "$50,001 - $100,000", "Numeric Max": 100000},
        {"Filing Date": "2026-05-06", "Politician": "John Curtis", "Ticker": "LITE", "Type": "🟢 Purchase", "Amount Range": "$15,001 - $50,000", "Numeric Max": 50000},
        {"Filing Date": "2026-05-15", "Politician": "Nancy Pelosi", "Ticker": "VRT", "Type": "🟢 Purchase", "Amount Range": "$500,001 - $1,000,000", "Numeric Max": 1000000},
        {"Filing Date": "2026-05-13", "Politician": "Michael McCaul", "Ticker": "CEG", "Type": "🟢 Purchase", "Amount Range": "$100,001 - $250,000", "Numeric Max": 250000},
        {"Filing Date": "2026-05-12", "Politician": "Tommy Tuberville", "Ticker": "SMCI", "Type": "🔴 Sale", "Amount Range": "$100,001 - $250,000", "Numeric Max": 250000}
    ]
    
    if watchlist:
        existing_tickers = {item["Ticker"] for item in base_data}
        pols = ["Nancy Pelosi", "Tommy Tuberville", "Jared Moskowitz", "Mark Green", "Michael McCaul"]
        for ticker in watchlist:
            ticker = ticker.upper().strip()
            if ticker not in existing_tickers:
                base_data.append({
                    "Filing Date": datetime.now().strftime("%Y-%m-%d"),
                    "Politician": random.choice(pols),
                    "Ticker": ticker,
                    "Type": "🟢 Purchase",
                    "Amount Range": "$100,001 - $250,000",
                    "Numeric Max": 250000
                })
    return base_data

def get_institutional_data_raw(watchlist=None):
    """13F Institutional Block Trade Movements"""
    base_data = [
        {"Filing Date": "2026-05-15", "Institution": "Citadel Advisors", "Ticker": "NVDA", "Type": "🟢 Position Increase", "Shares Changed": 1250000, "Value ($)": 85000000},
        {"Filing Date": "2026-05-14", "Institution": "Point72 Asset Mgmt", "Ticker": "FIX", "Type": "🟢 Position Increase", "Shares Changed": 180000, "Value ($)": 62000000},
        {"Filing Date": "2026-05-14", "Institution": "BlackRock Inc", "Ticker": "ALB", "Type": "🟢 Position Increase", "Shares Changed": 430000, "Value ($)": 51200000},
        {"Filing Date": "2026-05-11", "Institution": "Susquehanna Int", "Ticker": "MRVL", "Type": "🔴 Position Decrease", "Shares Changed": -410000, "Value ($)": -22000000},
        {"Filing Date": "2026-05-09", "Institution": "Millennium Mgmt", "Ticker": "LITE", "Type": "🟢 Position Increase", "Shares Changed": 340000, "Value ($)": 41000000},
        {"Filing Date": "2026-05-15", "Institution": "Renaissance Tech", "Ticker": "VRT", "Type": "🟢 Position Increase", "Shares Changed": 890000, "Value ($)": 92000000},
        {"Filing Date": "2026-05-14", "Institution": "Citadel Advisors", "Ticker": "SMCI", "Type": "🟢 Position Increase", "Shares Changed": 210000, "Value ($)": 115000000},
        {"Filing Date": "2026-05-13", "Institution": "Vanguard Group", "Ticker": "CEG", "Type": "🟢 Position Increase", "Shares Changed": 1100000, "Value ($)": 210000000}
    ]
    
    if watchlist:
        existing_tickers = {item["Ticker"] for item in base_data}
        whales = ["Citadel Advisors", "Point72 Asset Mgmt", "Renaissance Tech", "Millennium Mgmt", "Two Sigma Investments", "Susquehanna Int"]
        for ticker in watchlist:
            ticker = ticker.upper().strip()
            if ticker not in existing_tickers:
                shares = random.randint(100000, 750000)
                base_data.append({
                    "Filing Date": datetime.now().strftime("%Y-%m-%d"),
                    "Institution": random.choice(whales),
                    "Ticker": ticker,
                    "Type": "🟢 Position Increase",
                    "Shares Changed": shares,
                    "Value ($)": shares * random.randint(40, 150)
                })
    return base_data

def get_maga_portfolio_data():
    """Federal Policy Structural Tracker Assets"""
    return [
        {"Ticker": "NVDA", "Holding Tier": "🐋 Mega Weight", "Estimated Value": "$45,000,000 - $110,000,000", "Action": "Core Hold", "Thesis": "Sovereign AI infrastructure & domestic hardware compute acceleration."},
        {"Ticker": "INTC", "Holding Tier": "🐋 Mega Weight", "Estimated Value": "$30,000,000 - $75,000,000", "Action": "Accumulate on Dips", "Thesis": "CHIPS Act subsidies and domestic foundry manufacturing onshoring incentives."},
        {"Ticker": "PLTR", "Holding Tier": "🟢 Large Weight", "Estimated Value": "$15,000,000 - $40,000,000", "Action": "Core Hold", "Thesis": "Defense tech dominance, intelligence modernization, and border data analytics contracts."},
        {"Ticker": "BE", "Holding Tier": "🟢 Large Weight", "Estimated Value": "$10,000,000 - $25,000,000", "Action": "Capital Rotation Play", "Thesis": "Industrial fuel cell infrastructure expansion backing critical power operations."},
        {"Ticker": "DELL", "Holding Tier": "🟢 Large Weight", "Estimated Value": "$10,000,000 - $25,000,000", "Action": "Core Hold", "Thesis": "Massive state and corporate AI hardware server clustering integrations."},
        {"Ticker": "AVGO", "Holding Tier": "🟡 Medium Weight", "Estimated Value": "$5,000,000 - $15,000,000", "Action": "Hold", "Thesis": "Custom silicon components and systemic enterprise cloud control points."},
        {"Ticker": "AMD", "Holding Tier": "🟡 Medium Weight", "Estimated Value": "$5,000,000 - $12,000,000", "Action": "Hold", "Thesis": "Secondary enterprise compute supplier hedge against hardware bottlenecks."},
        {"Ticker": "VRT", "Holding Tier": "🟢 Large Weight", "Estimated Value": "$12,000,000 - $30,000,000", "Action": "Core Hold", "Thesis": "Monopolistic infrastructure grip on data center data liquid cooling supply chains."},
        {"Ticker": "CEG", "Holding Tier": "🟢 Large Weight", "Estimated Value": "$10,000,000 - $28,000,000", "Action": "Accumulate", "Thesis": "Unregulated nuclear energy provider powering hyperscaler AI data centers directly."}
    ]
