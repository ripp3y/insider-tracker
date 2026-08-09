import pandas as pd
import streamlit as st
import yfinance as yf

# App Layout Title
st.title("Algorithmic Signal Tracker")

# User input for asset ticker
ticker_symbol = st.text_input("Enter Ticker Symbol", value="NVDA")

@st.cache_data
def load_and_calculate_signals(ticker):
    # Fetch historical data using yfinance
    df = yf.download(ticker, period="6mo", interval="1d")
    
    # Flatten multi-index columns if returned by yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    # 1. Trend Basis (Fast & Slow EMA)
    df['EMA_Fast'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA_Slow'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    # 2. Momentum Proxy (MACD Histogram)
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = macd - signal_line
    
    # 3. Conditions & Crossovers
    trend_up = df['EMA_Fast'] > df['EMA_Slow']
    trend_dn = df['EMA_Fast'] < df['EMA_Slow']
    momentum_up = df['MACD_Hist'] > 0
    momentum_dn = df['MACD_Hist'] < 0
    
    crossover = (df['EMA_Fast'] > df['EMA_Slow']) & (df['EMA_Fast'].shift(1) <= df['EMA_Slow'].shift(1))
    crossunder = (df['EMA_Fast'] < df['EMA_Slow']) & (df['EMA_Fast'].shift(1) >= df['EMA_Slow'].shift(1))
    
    df['Signal'] = "HOLD"
    df.loc[crossover & trend_up & momentum_up, 'Signal'] = "BUY"
    df.loc[crossunder & trend_dn & momentum_dn, 'Signal'] = "SELL"
    
    return df

if ticker_symbol:
    data = load_and_calculate_signals(ticker_symbol)
    
    # Display recent signal history
    st.subheader(f"Recent Signals for {ticker_symbol.upper()}")
    active_signals = data[data['Signal'] != "HOLD"].tail(10)
    
    if not active_signals.empty:
        st.dataframe(active_signals[['Close', 'EMA_Fast', 'EMA_Slow', 'Signal']])
    else:
        st.info("No active BUY/SELL crossover signals found in the recent window.")
        
    # Display raw price chart with indicators
    st.line_chart(data[['Close', 'EMA_Fast', 'EMA_Slow']])
    if not active_signals.empty:
        st.dataframe(active_signals[['Close', 'EMA_Fast', 'EMA_Slow', 'Signal']])
    else:
        st.info("No active BUY/SELL crossover signals found in the recent window.")
        
    # Display raw price chart with indicators
    st.line_chart(data[['Close', 'EMA_Fast', 'EMA_Slow']])

    # --- APPEND THIS AT THE VERY END OF YOUR FILE ---
    signal_history = data[data['Signal'] != "HOLD"]

    st.subheader("🎯 Triggered Buy & Sell Signals")

    if not signal_history.empty:
        st.dataframe(
            signal_history[['Close', 'EMA_Fast', 'EMA_Slow', 'Signal']],
            use_container_width=True
        )
        
        latest_signal = signal_history.iloc[-1]
        signal_color = "green" if latest_signal['Signal'] == "BUY" else "red"
        st.markdown(f"Latest Signal Status: **:{signal_color}[{latest_signal['Signal']}]** at price **${latest_signal['Close']:.2f}**")
    else:
        st.info("No active crossover signals match the criteria in the selected timeframe.")
