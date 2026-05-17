# data_store.py
import json
import pandas as pd
from urllib.request import Request, urlopen

def get_insider_data_raw(watchlist_symbols=None):
    # Corporate insider master matrix (SEC Form 4)
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
    # STOCK Act political trade disclosures matrix
    poly_data = [
        {"Filing Date": "2026-05-14", "Ticker": "NVDA", "Politician": "Pelosi Nancy", "Chamber": "House", "Transaction": "🟢 Purchase", "Est. Amount": "$500,001 - $1,000,000"},
        {"Filing Date": "2026-05-12", "Ticker": "INTC", "Politician": "Tuberville Tommy", "Chamber": "Senate", "Transaction": "🔴 Sale", "Est. Amount": "$100,001 - $250,000"},
        {"Filing Date": "2026-05-10", "Ticker": "MRVL", "Politician": "McCaul Michael", "Chamber": "House", "Transaction": "🟢 Purchase", "Est. Amount": "$50,001 - $100,000"},
        {"Filing Date": "2026-04-28", "Ticker": "LITE", "Politician": "Khanna Ro", "Chamber": "House", "Transaction": "🔴 Sale", "Est
