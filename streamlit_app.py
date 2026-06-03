@st.cache_data(ttl=900)
def fetch_squeeze_telemetry(watchlist):
    records = []
    
    for ticker in watchlist:
        try:
            tk = yf.Ticker(ticker)
            info = tk.info
            hist = tk.history(period="3mo")
            
            # Catch empty info dictionaries or API blocks early
            if not info or len(info) <= 5 or hist.empty:
                continue
                
            # Compute current technical layers
            hist['RSI'] = calculate_rsi(hist['Close'])
            current_rsi = float(hist['RSI'].iloc[-1]) if not hist['RSI'].empty else 50.0
            current_price = float(hist['Close'].iloc[-1])
            
            # Safely extract short float percentage with secondary key check
            short_pct = info.get("shortPercentOfFloat", info.get("shortPercentOfFloat", 0.0))
            if short_pct is None: 
                short_pct = 0.0
            short_pct = short_pct * 100 if short_pct <= 1.0 else short_pct
            
            # Safely extract Institutional ownership matrix
            inst_pct = info.get("heldPercentInstitutions", info.get("institutionPercentHeld", 0.0))
            if inst_pct is None: 
                inst_pct = 0.0
            inst_pct = inst_pct * 100 if inst_pct <= 1.0 else inst_pct
            
            # Safely determine Days to Cover with robust fallbacks
            shares_short = info.get("sharesShort", 0) or 0
            daily_vol = info.get("averageVolume", info.get("averageVolume10Day", 1)) or 1
            days_to_cover = round(shares_short / daily_vol, 2) if shares_short > 0 else 0.0
            
            # Handle edge cases where short metrics are completely obfuscated
            if short_pct == 0.0 and days_to_cover > 0:
                # Approximate short float if raw percent is missing but short shares exist
                float_est = info.get("float", info.get("impliedSharesOutstanding", 1)) or 1
                short_pct = round((shares_short / float_est) * 100, 2)

            # Algorithmic Squeeze Priority Score
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
            # Print to terminal log to see exactly which ticker API is chocking
            print(f"Proxy error logging tracker for {ticker}: {str(e)}")
            
    return pd.DataFrame(records)
