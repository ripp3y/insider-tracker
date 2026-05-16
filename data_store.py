from datetime import datetime, timedelta

TODAY = datetime.now()

# Master Sector Mapping Database
SECTOR_MAP = {
    "NVDA": "Semiconductors / AI",
    "MRVL": "Semiconductors / AI",
    "UMC": "Semiconductors / AI",
    "LITE": "Optical Tech / Telecom",
    "FIX": "Industrial Infrastructure",
    "POWL": "Industrial Infrastructure",
    "BE": "Clean Energy / Utilities",
    "ALB": "Specialty Chemicals / Mining",
    "STX": "Data Storage / Hardware",
    "SNDK": "Data Storage / Hardware",
    "MSFT": "Enterprise Software / Cloud",
    "TXN": "Semiconductors / AI",
    "LRN": "EdTech / Services"
}

def get_fallback_political_data():
    return [
        {"Filing Date": TODAY - timedelta(days=0), "Politician": "Nancy Pelosi", "Chamber": "House", "Ticker": "NVDA", "Type": "🟢 Purchase", "Amount Range": "$1,000,001 - $5,000,000", "Numeric Max": 5000000},
        {"Filing Date": TODAY - timedelta(days=1), "Politician": "Markwayne Mullin", "Chamber": "Senate", "Ticker": "LRN", "Type": "🟢 Purchase", "Amount Range": "$15,001 - $50,001", "Numeric Max": 50000},
        {"Filing Date": TODAY - timedelta(days=2), "Politician": "Tommy Tuberville", "Chamber": "Senate", "Ticker": "TXN", "Type": "🟢 Purchase", "Amount Range": "$100,001 - $250,000", "Numeric Max": 250000},
        {"Filing Date": TODAY - timedelta(days=2), "Politician": "Tommy Tuberville", "Chamber": "Senate", "Ticker": "POWL", "Type": "🟢 Purchase", "Amount Range": "$50,001 - $100,000", "Numeric Max": 100000},
        {"Filing Date": TODAY - timedelta(days=3), "Politician": "Sheldon Whitehouse", "Chamber": "Senate", "Ticker": "MSFT", "Type": "🔴 Sale", "Amount Range": "$50,001 - $100,000", "Numeric Max": 100000},
        {"Filing Date": TODAY - timedelta(days=4), "Politician": "Michael Guest", "Chamber": "House", "Ticker": "FIX", "Type": "🟢 Purchase", "Amount Range": "$1,001 - $15,000", "Numeric Max": 15000},
        {"Filing Date": TODAY - timedelta(days=5), "Politician": "John Curtis", "Chamber": "House", "Ticker": "NVDA", "Type": "🟢 Purchase", "Amount Range": "$15,001 - $50,001", "Numeric Max": 50000},
        {"Filing Date": TODAY - timedelta(days=6), "Politician": "Markwayne Mullin", "Chamber": "Senate", "Ticker": "BE", "Type": "🟢 Purchase", "Amount Range": "$15,001 - $50,001", "Numeric Max": 50000},
        {"Filing Date": TODAY - timedelta(days=8), "Politician": "Ro Khanna", "Chamber": "House", "Ticker": "MRVL", "Type": "🔴 Sale", "Amount Range": "$50,001 - $100,000", "Numeric Max": 100000},
        {"Filing Date": TODAY - timedelta(days=11), "Politician": "Thomas Carper", "Chamber": "Senate", "Ticker": "ALB", "Type": "🟢 Purchase", "Amount Range": "$1,001 - $15,000", "Numeric Max": 15000},
        {"Filing Date": TODAY - timedelta(days=12), "Politician": "Dan Meuser", "Chamber": "House", "Ticker": "LITE", "Type": "🟢 Purchase", "Amount Range": "$50,001 - $100,000", "Numeric Max": 100000}
    ]

def get_insider_data_raw():
    return [
        {"Ticker": "LITE", "Company": "Lumentum Holdings", "Insider": "Alan Lowe", "Role": "CEO", "Type": "🟢 Buy", "Value ($)": 250000, "Filing Date": (TODAY - timedelta(days=1)).strftime('%Y-%m-%d')},
        {"Ticker": "FIX", "Company": "Comfort Systems USA", "Insider": "Brian Lane", "Role": "CEO", "Type": "🟢 Buy", "Value ($)": 1100000, "Filing Date": (TODAY - timedelta(days=3)).strftime('%Y-%m-%d')},
        {"Ticker": "MRVL", "Company": "Marvell Technology", "Insider": "Matt Murphy", "Role": "CEO", "Type": "🟢 Buy", "Value ($)": 450000, "Filing Date": (TODAY - timedelta(days=4)).strftime('%Y-%m-%d')},
        {"Ticker": "BE", "Company": "Bloom Energy", "Insider": "KR Sridhar", "Role": "CEO", "Type": "🔴 Sell (10b5-1)", "Value ($)": -120000, "Filing Date": (TODAY - timedelta(days=5)).strftime('%Y-%m-%d')},
        {"Ticker": "NVDA", "Company": "NVIDIA Corp", "Insider": "Colette Kress", "Role": "CFO", "Type": "🔴 Sell", "Value ($)": -2300000, "Filing Date": (TODAY - timedelta(days=7)).strftime('%Y-%m-%d')},
        {"Ticker": "POWL", "Company": "Powell Industries", "Insider": "Brett Cope", "Role": "CEO", "Type": "🟢 Buy", "Value ($)": 320000, "Filing Date": (TODAY - timedelta(days=10)).strftime('%Y-%m-%d')},
        {"Ticker": "ALB", "Company": "Albemarle Corp", "Insider": "Kent Masters", "Role": "CEO", "Type": "🟢 Buy", "Value ($)": 500000, "Filing Date": (TODAY - timedelta(days=12)).strftime('%Y-%m-%d')}
    ]

def get_institutional_data_raw():
    return [
        {"Filing Date": (TODAY - timedelta(days=1)).strftime('%Y-%m-%d'), "Ticker": "STX", "Institution": "BlackRock Inc.", "Type": "🟢 Position Increase", "Shares Changed": 1250000, "Value ($)": 85000000},
        {"Filing Date": (TODAY - timedelta(days=2)).strftime('%Y-%m-%d'), "Ticker": "NVDA", "Institution": "Vanguard Group", "Type": "🟢 Position Increase", "Shares Changed": 4300000, "Value ($)": 512000000},
        {"Filing Date": (TODAY - timedelta(days=3)).strftime('%Y-%m-%d'), "Ticker": "FIX", "Institution": "Fidelity Management", "Type": "🟢 Position Increase", "Shares Changed": 180000, "Value ($)": 62000000},
        {"Filing Date": (TODAY - timedelta(days=5)).strftime('%Y-%m-%d'), "Ticker": "MRVL", "Institution": "Renaissance Technologies", "Type": "🟢 Position Increase", "Shares Changed": 850000, "Value ($)": 55000000},
        {"Filing Date": (TODAY - timedelta(days=6)).strftime('%Y-%m-%d'), "Ticker": "ALB", "Institution": "Citadel Advisors", "Type": "🟢 Position Increase", "Shares Changed": 340000, "Value ($)": 41000000},
        {"Filing Date": (TODAY - timedelta(days=9)).strftime('%Y-%m-%d'), "Ticker": "LITE", "Institution": "Point72 Asset Mgmt", "Type": "🔴 Position Decrease", "Shares Changed": -410000, "Value ($)": -22000000}
    ]
