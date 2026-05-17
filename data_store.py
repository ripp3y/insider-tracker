# data_store.py

def get_insider_data_raw(watchlist_symbols=None):
    # Comprehensive master matrix for corporate insider filings (Form 4)
    insider_data = [
        {"Filing Date": "2026-05-15", "Ticker": "ALB", "Insider": "Masters Eric", "Role": "Director", "Value ($)": 145000},
        {"Filing Date": "2026-05-14", "Ticker": "FIX", "Insider": "Garner William", "Role": "VP / COO", "Value ($)": 620000},
        {"Filing Date": "2026-05-12", "Ticker": "NVDA", "Insider": "Huang Jen-Hsun", "Role": "CEO", "Value ($)": 12500000},
        {"Filing Date": "2026-05-11", "Ticker": "MRVL", "Insider": "Murphy Matt", "Role": "CEO", "Value ($)": 480000},
        {"Filing Date": "2026-05-08", "Ticker": "POWL", "Insider": "Powell Brett", "Role": "Director", "Value ($)": -310000},
        {"Filing Date": "2026-05-05", "Ticker": "LITE", "Insider": "Lowe Alan", "Role": "CEO", "Value ($)": 185000},
        {"Filing Date": "2026-05-11", "Ticker": "MU", "Insider": "Mehrotra Sanjay", "Role": "CEO", "Value ($)": 890000},
        {"Filing Date": "2026-05-17", "Ticker": "INTC", "Insider": "Blackstone Group", "Role": "Chief Financial", "Value ($)": 2500000},
        {"Filing Date": "2026-05-17", "Ticker": "AMD", "Insider": "Sovereign Asset Mgmt", "Role": "CEO / Presi", "Value ($)": -1200000},
        {"Filing Date": "2026-05-17", "Ticker": "FN", "Insider": "Apex Holdings", "Role": "Director", "Value ($)": 350000}
    ]
    if watchlist_symbols:
        return [row for row in insider_data if row["Ticker"] in watchlist_symbols]
    return insider_data


def get_fallback_political_data(watchlist_symbols=None):
    # Master matrix for STOCK Act political trade disclosures
    poly_data = [
        {"Filing Date": "2026-05-14", "Ticker": "NVDA", "Politician": "Pelosi Nancy", "Chamber": "House", "Transaction": "🟢 Purchase", "Est. Amount": "$500,001 - $1,000,000"},
        {"Filing Date": "2026-05-12", "Ticker": "INTC", "Politician": "Tuberville Tommy", "Chamber": "Senate", "Transaction": "🔴 Sale", "Est. Amount": "$100,001 - $250,000"},
        {"Filing Date": "2026-05-10", "Ticker": "MRVL", "Politician": "McCaul Michael", "Chamber": "House", "Transaction": "🟢 Purchase", "Est. Amount": "$50,001 - $100,000"},
        {"Filing Date": "2026-05-04", "Ticker": "ALB", "Politician": "Carper Thomas", "Chamber": "Senate", "Transaction": "🟢 Purchase", "Est. Amount": "$15,001 - $50,000"},
        {"Filing Date": "2026-04-28", "Ticker": "LITE", "Politician": "Khanna Ro", "Chamber": "House", "Transaction": "🔴 Sale", "Est. Amount": "$100,001 - $250,000"}
    ]
    if watchlist_symbols:
        return [row for row in poly_data if row["Ticker"] in watchlist_symbols]
    return poly_data


def get_institutional_data_raw(watchlist_symbols=None):
    # New deep matrix for institutional whale blocks (13F, 13D, 13G)
    whale_data = [
        {"Ticker": "NVDA", "Whale/Fund": "Citadel Advisors", "Type": "13F", "Change Direction": "🟢 Accumulation", "Shares Changed": 1250000, "Value ($)": 115000000, "Report Date": "2026-05-15"},
        {"Ticker": "NVDA", "Whale/Fund": "Renaissance Technologies", "Type": "13F", "Change Direction": "🔴 Reduction", "Shares Changed": -450000, "Value ($)": 41400000, "Report Date": "2026-05-14"},
        {"Ticker": "INTC", "Whale/Fund": "BlackRock Inc.", "Type": "13F", "Change Direction": "🟢 Accumulation", "Shares Changed": 3400000, "Value ($)": 102000000, "Report Date": "2026-05-15"},
        {"Ticker": "MRVL", "Whale/Fund": "Point72 Asset Mgmt", "Type": "13D (Active)", "Change Direction": "🟢 Material Buy", "Shares Changed": 850000, "Value ($)": 59500000, "Report Date": "2026-05-12"},
        {"Ticker": "FIX", "Whale/Fund": "Vanguard Group", "Type": "13F", "Change Direction": "🟢 Accumulation", "Shares Changed": 120000, "Value ($)": 42000000, "Report Date": "2026-05-10"},
        {"Ticker": "ALB", "Whale/Fund": "Coatue Management", "Type": "13G (Passive)", "Change Direction": "🔴 Disposal", "Shares Changed": -600000, "Value ($)": 72000000, "Report Date": "2026-05-11"},
        {"Ticker": "LITE", "Whale/Fund": "Millennium Management", "Type": "13F", "Change Direction": "🟢 Accumulation", "Shares Changed": 310000, "Value ($)": 18600000, "Report Date": "2026-05-08"},
    ]
    if watchlist_symbols:
        return [row for row in whale_data if row["Ticker"] in watchlist_symbols]
    return whale_data


def get_maga_portfolio_data():
    # Static legislative index feed mapping
    return [
        {"Ticker": "NVDA", "Holding Sizing": "Top 5 Overweight", "Policy Catalyst": "AI Infrastructure Subsidies"},
        {"Ticker": "INTC", "Holding Sizing": "Core Long", "Policy Catalyst": "Domestic Foundry Tax Credits"},
        {"Ticker": "FIX", "Holding Sizing": "Industrial Weight", "Policy Catalyst": "Grid Resiliency / Onshoring Capital"}
    ]


def get_sector(ticker):
    # Global sector mapping catalog
    sectors = {
        "NVDA": "Semiconductors / AI Infrastructure",
        "INTC": "Semiconductors / Foundry",
        "MRVL": "Data Infrastructure / Silicon",
        "FIX": "Building Infrastructure / Facilities",
        "ALB": "Lithium Mining / Commodities",
        "LITE": "Optical Components / Laser Tech"
    }
    return sectors.get(ticker, "General Equities")
