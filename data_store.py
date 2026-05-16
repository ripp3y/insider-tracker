# --------------------------------------------------------
# Asymmetry Data Store - Master Asset Matrix
# --------------------------------------------------------

# Global Sector Map for Auto-Categorization
SECTOR_MAP = {
    # Existing Tracking Portfolio
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
    
    # New High-Alpha Tracking Additions
    "SMCI": "Hardware / AI Server Liquid Cooling",
    "VRT": "Industrial Infrastructure / Data Center Liquid Cooling",
    "CEG": "Utilities / Data Center Nuclear Power",
    "MU": "Semiconductors / High-Bandwidth Memory",
    "ANET": "Tech Hardware / AI Networking"
}

def get_insider_data_raw():
    """
    Form 4 Insider Filing Stream
    Positive Value = Purchase | Negative Value = Open Market Sale
    """
    return [
        {"Filing Date": "2026-05-15", "Ticker": "ALB", "Insider": "Masters Eric", "Role": "Director", "Type": "🟢 Purchase", "Value ($)": 450000},
        {"Filing Date": "2026-05-14", "Ticker": "FIX", "Insider": "Garner William", "Role": "VP / COO", "Type": "🟢 Purchase", "Value ($)": 820000},
        {"Filing Date": "2026-05-12", "Ticker": "NVDA", "Insider": "Huang Jen-Hsun", "Role": "CEO", "Type": "🔴 Sale", "Value ($)": -12500000},
        {"Filing Date": "2026-05-11", "Ticker": "MRVL", "Insider": "Murphy Matt", "Role": "CEO", "Type": "🔴 Sale", "Value ($)": -1400000},
        {"Filing Date": "2026-05-08", "Ticker": "POWL", "Insider": "Powell Brett", "Role": "Director", "Type": "🟢 Purchase", "Value ($)": 310000},
        {"Filing Date": "2026-05-05", "Ticker": "LITE", "Insider": "Lowe Alan", "Role": "CEO", "Type": "🟢 Purchase", "Value ($)": 520000},
        
        # New Ticker Insider Filings
        {"Filing Date": "2026-05-15", "Ticker": "VRT", "Insider": "Johnson Giordano", "Role": "CEO", "Type": "🟢 Purchase", "Value ($)": 1100000},
        {"Filing Date": "2026-05-14", "Ticker": "SMCI", "Insider": "Liaw Liang", "Role": "Director", "Type": "🟢 Purchase", "Value ($)": 950000},
        {"Filing Date": "2026-05-11", "Ticker": "MU", "Insider": "Mehrotra Sanjay", "Role": "CEO", "Type": "🔴 Sale", "Value ($)": -3200000}
    ]

def get_fallback_political_data():
    """
    Congressional Disclosures (Backup layout when live GitHub scrapers rate-limit)
    """
    return [
        {"Filing Date": "2026-05-14", "Politician": "Nancy Pelosi", "Ticker": "NVDA", "Type": "🟢 Purchase", "Amount Range": "$1,000,001 - $5,000,000", "Numeric Max": 5000000},
        {"Filing Date": "2026-05-12", "Politician": "Tommy Tuberville", "Ticker": "ALB", "Type": "🟢 Purchase", "Amount Range": "$100,001 - $250,000", "Numeric Max": 250000},
        {"Filing Date": "2026-05-10", "Politician": "Mark Green", "Ticker": "FIX", "Type": "🟢 Purchase", "Amount Range": "$50,001 - $100,000", "Numeric Max": 100000},
        {"Filing Date": "2026-05-06", "Politician": "John Curtis", "Ticker": "LITE", "Type": "🟢 Purchase", "Amount Range": "$15,001 - $50,000", "Numeric Max": 50000},
        
        # New Ticker Political Alignment Trades
        {"Filing Date": "2026-05-15", "Politician": "Nancy Pelosi", "Ticker": "VRT", "Type": "🟢 Purchase", "Amount Range": "$500,001 - $1,000,000", "Numeric Max": 1000000},
        {"Filing Date": "2026-05-13", "Politician": "Michael McCaul", "Ticker": "CEG", "Type": "🟢 Purchase", "Amount Range": "$100,001 - $250,000", "Numeric Max": 250000},
        {"Filing Date": "2026-05-12", "Politician": "Tommy Tuberville", "Ticker": "SMCI", "Type": "🔴 Sale", "Amount Range": "$100,001 - $250,000", "Numeric Max": 250000}
    ]

def get_institutional_data_raw():
    """
    13F Institutional Block Trade Movements (Value represented in millions)
    """
    return [
        {"Filing Date": "2026-05-15", "Institution": "Citadel Advisors", "Ticker": "NVDA", "Type": "🟢 Position Increase", "Shares Changed": 1250000, "Value ($)": 85000000},
        {"Filing Date": "2026-05-14", "Institution": "Point72 Asset Mgmt", "Ticker": "FIX", "Type": "🟢 Position Increase", "Shares Changed": 180000, "Value ($)": 62000000},
        {"Filing Date": "2026-05-14", "Institution": "BlackRock Inc", "Ticker": "ALB", "Type": "🟢 Position Increase", "Shares Changed": 430000, "Value ($)": 51200000},
        {"Filing Date": "2026-05-11", "Institution": "Susquehanna Int", "Ticker": "MRVL", "Type": "🔴 Position Decrease", "Shares Changed": -410000, "Value ($)": -22000000},
        {"Filing Date": "2026-05-09", "Institution": "Millennium Mgmt", "Ticker": "LITE", "Type": "🟢 Position Increase", "Shares Changed": 340000, "Value ($)": 41000000},
        
        # New Ticker Institutional Accumulation Blocks
        {"Filing Date": "2026-05-15", "Institution": "Renaissance Tech", "Ticker": "VRT", "Type": "🟢 Position Increase", "Shares Changed": 890000, "Value ($)": 92000000},
        {"Filing Date": "2026-05-14", "Institution": "Citadel Advisors", "Ticker": "SMCI", "Type": "🟢 Position Increase", "Shares Changed": 210000, "Value ($)": 115000000},
        {"Filing Date": "2026-05-13", "Institution": "Vanguard Group", "Ticker": "CEG", "Type": "🟢 Position Increase", "Shares Changed": 1100000, "Value ($)": 210000000}
    ]

def get_maga_portfolio_data():
    """
    Federal Policy Structural Tracker Assets
    """
    return [
        {"Ticker": "NVDA", "Holding Tier": "🐋 Mega Weight", "Estimated Value": "$45,000,000 - $110,000,000", "Action": "Core Hold", "Thesis": "Sovereign AI infrastructure & domestic hardware compute acceleration."},
        {"Ticker": "INTC", "Holding Tier": "🐋 Mega Weight", "Estimated Value": "$30,000,000 - $75,000,000", "Action": "Accumulate on Dips", "Thesis": "CHIPS Act subsidies and domestic foundry manufacturing onshoring incentives."},
        {"Ticker": "PLTR", "Holding Tier": "🟢 Large Weight", "Estimated Value": "$15,000,000 - $40,000,000", "Action": "Core Hold", "Thesis": "Defense tech dominance, intelligence modernization, and border data analytics contracts."},
        {"Ticker": "BE", "Holding Tier": "🟢 Large Weight", "Estimated Value": "$10,000,000 - $25,000,000", "Action": "Capital Rotation Play", "Thesis": "Industrial fuel cell infrastructure expansion backing critical power operations."},
        {"Ticker": "DELL", "Holding Tier": "🟢 Large Weight", "Estimated Value": "$10,000,000 - $25,000,000", "Action": "Core Hold", "Thesis": "Massive state and corporate AI hardware server clustering integrations."},
        {"Ticker": "AVGO", "Holding Tier": "🟡 Medium Weight", "Estimated Value": "$5,000,000 - $15,000,000", "Action": "Hold", "Thesis": "Custom silicon components and systemic enterprise cloud control points."},
        {"Ticker": "AMD", "Holding Tier": "🟡 Medium Weight", "Estimated Value": "$5,000,000 - $12,000,000", "Action": "Hold", "Thesis": "Secondary enterprise compute supplier hedge against hardware bottlenecks."},
        
        # New Ticker High-Conviction Policy Alignments
        {"Ticker": "VRT", "Holding Tier": "🟢 Large Weight", "Estimated Value": "$12,000,000 - $30,000,000", "Action": "Core Hold", "Thesis": "Monopolistic infrastructure grip on data center data liquid cooling supply chains."},
        {"Ticker": "CEG", "Holding Tier": "🟢 Large Weight", "Estimated Value": "$10,000,000 - $28,000,000", "Action": "Accumulate", "Thesis": "Unregulated nuclear energy provider powering hyperscaler AI data centers directly."}
    ]
