import pandas as pd
import requests
import yfinance as yf
import streamlit as st
import os
from datetime import datetime

# Block concurrent background tracking files from throwing SQLite database lock errors
os.environ["YFINANCE_CACHE"] = "FALSE"

@st.cache_data(ttl=300)
def fetch_live_market_prices(tickers):
    """
    Safely queries yfinance 1-day interval targets using linear single-thread requests.
    """
    try:
        ticker_list = list(tickers) if not isinstance(tickers, list) else tickers
        if not ticker_list:
            return {}
        
        # Enforce threads=False to completely isolate data reads from thread contentions
        data = yf.download(ticker_list, period="1d", progress=False, threads=False)
        
        if "Close" in data.columns:
            close_data = data["Close"].iloc[-1]
        else:
            close_data = data.iloc[-1]
            
        if isinstance(close_data, pd.Series):
            return {ticker: float(val) for ticker, val in close_data.to_dict().items() if pd.notna(val)}
        else:
            return {ticker_list[0]: float(close_data)}
    except Exception:
        return {}

def get_live_portfolio_positions():
    """
    Main positions matrix mapping real ledger structures to eliminate ticker parsing collisions.
    """
    portfolio_ledger = [
        # --- HEALTH SAVINGS ACCOUNT (HSA) ---
        {"Account": "HSA", "Ticker": "CIEN", "Shares": 11.615, "Cost Basis": 602.65},
        {"Account": "HSA", "Ticker": "FIX", "Shares": 2.828, "Cost Basis": 1769.94},
        {"Account": "HSA", "Ticker": "WOLF", "Shares": 28.398, "Cost Basis": 75.99},
        
        # --- BROKERAGELINK ACCOUNT ---
        {"Account": "BrokerageLink", "Ticker": "AXTI", "Shares": 17.878, "Cost Basis": 135.81},
        {"Account": "BrokerageLink", "Ticker": "BE", "Shares": 11.797, "Cost Basis": 307.61},
        {"Account": "BrokerageLink", "Ticker": "FIX", "Shares": 5.237, "Cost Basis": 1818.62},
        {"Account": "BrokerageLink", "Ticker": "LITE", "Shares": 3.604, "Cost Basis": 970.98},
        {"Account": "BrokerageLink", "Ticker": "MRVL", "Shares": 75.135, "Cost Basis": 133.09},
        {"Account": "BrokerageLink", "Ticker": "POWL", "Shares": 35.030, "Cost Basis": 285.47},
        {"Account": "BrokerageLink", "Ticker": "SNDK", "Shares": 8.540, "Cost Basis": 947.99},
        {"Account": "BrokerageLink", "Ticker": "STX", "Shares": 16.111, "Cost Basis": 500.45}
    ]
    
    df = pd.DataFrame(portfolio_ledger)
    unique_tickers = list(df["Ticker"].unique())
    price_map = fetch_live_market_prices(unique_tickers)
    
    # Air-gapped fallbacks taken directly from statement baselines to bypass server tracking blockades
    fallbacks = {
        "CIEN": 602.39,   "FIX": 1883.56,  "WOLF": 73.50, 
        "AXTI": 132.60,   "BE": 302.40,    "LITE": 910.81, 
        "MRVL": 208.26,   "POWL": 291.97,  "SNDK": 1589.55, 
        "STX": 845.76
    }
    
    df["Current Price"] = df["Ticker"].apply(lambda t: float(price_map.get(t, fallbacks.get(t, 0.0))))
    df["Total Value"] = df["Shares"] * df["Current Price"]
    df["Cost Basis Total"] = df["Shares"] * df["Cost Basis"]
    df["Total Gain ($)"] = df["Total Value"] - df["Cost Basis Total"]
    df["Total Gain (%)"] = (df["Total Gain ($)"] / df["Cost Basis Total"]) * 100
    
    return df.sort_values(by="Total Value", ascending=False).reset_index(drop=True)

@st.cache_data(ttl=600)
def get_live_technicals(watchlist):
    """
    Builds baseline EMA cross momentum matrices for custom tracked targets.
    """
    technical_rows = []
    if not watchlist:
        return pd.DataFrame()
        
    try:
        history = yf.download(list(watchlist), period="3mo", progress=False, threads=False)["Close"]
        for ticker in watchlist:
            if len(watchlist) == 1:
                series = history.dropna()
            elif ticker in history.columns:
                series = history[ticker].dropna()
            else:
                continue
                
            if len(series) >= 50:
                last_price = float(series.iloc[-1])
                ema21 = float(series.ewm(span=21, adjust=False).mean().iloc[-1])
                ema50 = float(series.ewm(span=50, adjust=False).mean().iloc[-1])
                
                if last_price > ema21 and ema21 > ema50:
                    setup = "🔥 Breakout"
                elif ema50 * 0.98 <= last_price <= ema21 * 1.02:
                    setup = "🟢 Entry Zone"
                else:
                    setup = "💤 Premium / Hold"
                    
                technical_rows.append({
                    "Ticker": ticker,
                    "Last Price": f"${last_price:,.2f}",
                    "21-day EMA": f"${ema21:,.2f}",
                    "50-day EMA": f"${ema50:,.2f}",
                    "Technical Setup": setup
                })
    except Exception:
        pass
        
    if technical_rows:
        return pd.DataFrame(technical_rows)
    return pd.DataFrame(columns=
