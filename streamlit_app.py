import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import yfinance as yf

# -----------------------------------------------------------------------------
# CORE ALGORITHMIC ENGINE
# -----------------------------------------------------------------------------
def calculate_rsi(series, period=14):
    """Computes standard 14-Day RSI to flag structural overbought/oversold nodes."""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / (loss + 1e-9) # Prevent divide-by-zero
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=900)
def fetch_squeeze_telemetry(watchlist):
    """
    Pulls live financial telemetry via Yahoo Finance API, mining short metrics,
    RSI momentum, and institutional accumulation footprints.
    """
    records = []
    
    for ticker in watchlist:
        try:
            tk = yf.Ticker(ticker)
            info = tk.info
            hist = tk.history(period="3mo")
            
            if hist.empty:
                continue
                
            # Compute current technical layers
            hist['RSI'] = calculate_rsi(hist['Close'])
            current_rsi = float(hist['RSI'].iloc[-1]) if not hist['RSI'].empty else 50.0
            current_price = float(hist['Close'].iloc[-1])
            
            # Extract Raw Short Interest & Institutional Float Layers
            short_pct = info.get("shortPercentOfFloat", 0.0) * 100  # Convert to standard %
            inst_pct = info.get("heldPercentInstitutions", 0.0) * 100
            shares_short = info.get("sharesShort", 0)
            avg_volume = info.get("impliedSharesOutstanding", 1)  # Fallback divisor
            
            # Estimate Days to Cover cleanly
            daily_vol = info.get("averageVolume", 1)
            days_to_cover = round(shares_short / daily_vol, 2) if daily_vol > 0 else 0.0
            
            # Algorithmic Squeeze Priority Score
            # Heavy weights applied to high short float combined with high institutional backing
            squeeze_score = (short_pct * 2.0) + (inst_pct * 0.5) + (days_to_cover * 1.5)
            if current_rsi < 35:  # Oversold kicker (spring loaded)
                squeeze_score += 15
            elif current_rsi > 75: # Hyper-extended warning
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
            pass # Keep terminal stream clean if a single API ticker fails
            
    return pd.DataFrame(records)

# -----------------------------------------------------------------------------
# INTERFACE RENDER LAYER
# -----------------------------------------------------------------------------
def render_squeeze_scanner_ui():
    st.markdown("## ⚡ Alpha Matrix: AI Institutional Short Squeeze Radar")
    st.markdown(
        "Tracking systemic blind spots where short-sellers are heavily exposed "
        "while institutional whales lock down the underlying float."
    )
    
    # Target candidates setting up across the broader AI ecosystem right now
    target_ai_pool = ["SOUN", "AI", "NVTS", "BBAI", "PLTR", "SMCI", "RUM", "PATH", "HOLO"]
    
    with st.spinner("Parsing market short-interest telemetry..."):
        df_metrics = fetch_squeeze_telemetry(target_ai_pool)
        
    if not df_metrics.empty:
        # Sort matrix cleanly by the highest computational vulnerability score
        df_metrics = df_metrics.sort_values(by="Squeeze Score", ascending=False)
        
        # 1. Plotly Data Visualization Component
        fig = px.scatter(
            df_metrics, 
            x="Short Float %", 
            y="Squeeze Score", 
            size="Days to Cover",
            color="14D RSI",
            hover_name="Ticker",
            text="Ticker",
            color_continuous_scale="Viridis",
            labels={"Short Float %": "Short Interest (% of Float)", "Squeeze Score": "Squeeze Priority Index"}
        )
        fig.update_traces(textposition="top center", marker=dict(line=dict(width=1, color='DarkSlateGrey')))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=30, b=10),
            height=380
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown("### 📊 Live Telemetry Logs")
        st.dataframe(
            df_metrics,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Squeeze Score": st.column_config.ProgressColumn(
                    "Squeeze Priority Index",
                    help="Calculated vulnerability matrix rating potential squeeze velocity",
                    format="%.1f",
                    min_value=0,
                    max_value=120,
                )
            }
        )
    else:
        st.error("Terminal failed to parse tracking hooks. Refresh data proxy engine.")

if __name__ == "__main__":
    render_squeeze_scanner_ui()
