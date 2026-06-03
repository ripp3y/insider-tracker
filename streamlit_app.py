import streamlit as st
import pandas as pd
import yfinance as yf

# Now your functions follow safely below...
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=900)
def fetch_squeeze_telemetry(watchlist):
    # rest of your code...


@st.cache_data(ttl=900)
def fetch_squeeze_telemetry(watchlist):
    # rest of your code...


# 1. DEFINE THIS FIRST: The technical calculator helper must execute before the cache wrapper initializes
def calculate_rsi(series, period=14):
    """Computes standard 14-Day RSI to flag structural overbought/oversold nodes."""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / (loss + 1e-9)  # Prevent divide-by-zero
    return 100 - (100 / (1 + rs))

# 2. DEFINE THIS SECOND: Caching wrapper can now safely map the dependent scope
@st.cache_data(ttl=900)
def fetch_squeeze_telemetry(watchlist):
    records = []
    for ticker in watchlist:
        try:
            tk = yf.Ticker(ticker)
            info = tk.info
            hist = tk.history(period="3mo")
            
            if not info or len(info) <= 5 or hist.empty:
                continue
                
            hist['RSI'] = calculate_rsi(hist['Close'])
            current_rsi = float(hist['RSI'].iloc[-1]) if not hist['RSI'].empty else 50.0
            current_price = float(hist['Close'].iloc[-1])
            
            # Key extraction with fallback maps
            short_pct = info.get("shortPercentOfFloat", info.get("shortPercentOfFloat", 0.0))
            if short_pct is None: 
                short_pct = 0.0
            short_pct = short_pct * 100 if short_pct <= 1.0 else short_pct
            
            inst_pct = info.get("heldPercentInstitutions", info.get("institutionPercentHeld", 0.0))
            if inst_pct is None: 
                inst_pct = 0.0
            inst_pct = inst_pct * 100 if inst_pct <= 1.0 else inst_pct
            
            shares_short = info.get("sharesShort", 0) or 0
            daily_vol = info.get("averageVolume", info.get("averageVolume10Day", 1)) or 1
            days_to_cover = round(shares_short / daily_vol, 2) if shares_short > 0 else 0.0
            
            if short_pct == 0.0 and days_to_cover > 0:
                float_est = info.get("float", info.get("impliedSharesOutstanding", 1)) or 1
                short_pct = round((shares_short / float_est) * 100, 2)

            squeeze_score = (short_pct * 2.0) + (inst_pct * 0.5) + (days_to_cover * 1.5)
            if current_rsi < 35:
                squeeze_score += 15
            elif current_rsi > 75:
                squeeze_score -= 10

            records.append({
                "Ticker": ticker,
                "Price": f"${current_price:,.2f}",
                "Short Float %": round(short_pct, 2),
                "Inst. Owned %": round(inst_pct, 2),
                "Days to Cover": days_to_cover,
                "14D RSI": round(current_rsi, 1),
                "Squeeze Score": round(squeeze_score, 2)
            })
        except Exception as e:
            print(f"Proxy log error for {ticker}: {str(e)}")
            
    return pd.DataFrame(records)
