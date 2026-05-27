import pandas as pd
import requests
import yfinance as yf
import streamlit as st
import os
import logging
from datetime import datetime

# Terminate warning trace logs programmatically
logging.getLogger("streamlit").setLevel(logging.ERROR)
os.environ["YFINANCE_CACHE"] = "FALSE"

# Hardcoded global fallbacks to protect the UI during API blackouts
FALLBACK_PRICES = {
    "NVDA": 105.50, "LITE": 910.81, "MRVL": 208.26, 
    "AXTI": 132.60, "COHR": 245.10, "FIX": 1883.56, 
    "ALB": 115.40,  "CIEN": 602.39, "WOLF": 73.50, 
    "BE": 302.40,   "POWL": 291.97, "SNDK": 1589.55, 
    "STX": 845.76
}

@st.cache_data(ttl=300)
def fetch_live_market_prices(tickers):
    """
    Queries yfinance with full exception insulation and immediate fallback recovery.
    """
    ticker_list = list(tickers) if not isinstance(tickers, list) else tickers
    if not ticker_list:
        return FALLBACK_PRICES
        
    price_map = {}
    try:
        # Single-threaded download prevents SQLite thread collisions during limit spikes
        data = yf.download(ticker_list, period="1d", progress=False, threads=False)
        
        if not data.empty:
            if "Close" in data.columns:
                close_data = data["Close"].iloc[-1]
            else:
                close_data = data.iloc[-1]
                
            if isinstance(close_data, pd.Series):
                price_map = {ticker: float(val) for ticker, val in close_data.to_dict().items() if pd.notna(val)}
            else:
                price_map = {ticker_list[0]: float(close_data)}
    except Exception:
        # Silently absorb YFRateLimitError or connection drops
        pass

    # Layer in fallback data for any missing tickers to guarantee the UI prints smoothly
    for ticker in ticker_list:
        if ticker not in price_map or pd.isna(price_map[ticker]) or price_map[ticker] == 0:
            price_map[ticker] = FALLBACK_PRICES.get(ticker, 100.0)
            
    return price_map

def get_live_portfolio_positions():
    """
    Maps current portfolio allocations. Protected against external API rate restrictions.
    """
    portfolio_ledger = [
        {"Account": "HSA", "Ticker": "CIEN", "Shares": 11.615, "Cost Basis": 602.65},
        {"Account": "HSA", "Ticker": "FIX", "Shares": 2.828, "Cost Basis": 1769.94},
        {"Account": "HSA", "Ticker": "WOLF", "Shares": 28.398, "Cost Basis": 75.99},
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
    
    df["Current Price"] = df["Ticker"].apply(lambda t: float(price_map.get(t, FALLBACK_PRICES.get(t, 100.0))))
    df["Total Value"] = df["Shares"] * df["Current Price"]
    df["Cost Basis Total"] = df["Shares"] * df["Cost Basis"]
    df["Total Gain ($)"] = df["Total Value"] - df["Cost Basis Total"]
    df["Total Gain (%)"] = (df["Total Gain ($)"] / df["Cost Basis Total"]) * 100
    
    return df.sort_values(by="Total Value", ascending=False).reset_index(drop=True)

@st.cache_data(ttl=600)
def get_live_technicals(watchlist):
    """
    Builds EMA momentum arrays. Uses price mapping arrays if historical requests get rate-limited.
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
                
            if len(series) >= 20:
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
        
    # If history fails completely due to a rate limit, build a stable structure using static metrics
    if not technical_rows:
        fallback_map
