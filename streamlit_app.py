import pandas as pd
import streamlit as st
import yfinance as yf

st.title("Algorithmic Signal Tracker")

ticker_symbol = st.text_input("Enter Ticker Symbol", value="NVDA")

@st.cache_data
def calculate_custom_strategy(ticker, period="6mo"):
    # Fetch historical data using yfinance
    df = yf.download(ticker, period=period, interval="1d")
    
    # Flatten multi-index columns if returned by yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    # 1. Fast & Slow EMA (5/13 setup)
    df['EMA_Fast'] = df['Close'].ewm(span=5, adjust=False).mean()
    df['EMA_Slow'] = df['Close'].ewm(span=13, adjust=False).mean()
    
    # 2. Momentum proxy (MACD Histogram)
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = macd - signal_line
    
    # 3. Signals
    trend_up = df['EMA_Fast'] > df['EMA_Slow']
    trend_dn = df['EMA_Fast'] < df['EMA_Slow']
    momentum_up = df['MACD_Hist'] > 0
    momentum_dn = df['MACD_Hist'] < 0
    
    crossover = (df['EMA_Fast'] > df['EMA_Slow']) & (df['EMA_Fast'].shift(1) <= df['EMA_Slow'].shift(1))
    crossunder = (df['EMA_Fast'] < df['EMA_Slow']) & (df['EMA_Fast'].shift(1) >= df['EMA_Slow'].shift(1))
    
    df['Signal'] = "HOLD"
    df.loc[crossover & trend_up & momentum_up, 'Signal'] = "BUY"
    df.loc[crossunder & trend_dn & momentum_dn, 'Signal'] = "SELL"
    
    # 4. Assign Trailing Stop Rules per Ticker (8% for WOLF and AXTI, 5% for others)
    if ticker.upper() in ["WOLF", "AXTI"]:
        trailing_pct = 0.08
    else:
        trailing_pct = 0.05
        
    df['Running_Max'] = df['Close'].cummax()
    df['Trailing_Stop_Price'] = df['Running_Max'] * (1 - trailing_pct)
    
    return df

if ticker_symbol:
    data = calculate_custom_strategy(ticker_symbol)
    
    # Display raw price chart with indicators
    st.line_chart(data[['Close', 'EMA_Fast', 'EMA_Slow']])

    # Filter and display triggered signals and trailing levels
    signal_history = data[data['Signal'] != "HOLD"]

    st.subheader("🎯 Triggered Signals & Stop Targets")

    if not signal_history.empty:
        st.dataframe(
            signal_history[['Close', 'EMA_Fast', 'EMA_Slow', 'Trailing_Stop_Price', 'Signal']],
            use_container_width=True
        )
        
        latest_signal = signal_history.iloc[-1]
        signal_color = "green" if latest_signal['Signal'] == "BUY" else "red"
        st.markdown(f"Latest Signal Status: **:{signal_color}[{latest_signal['Signal']}]** at price **${latest_signal['Close']:.2f}**")
        st.markdown(f"Current Dynamic Trailing Stop Target: **${latest_signal['Trailing_Stop_Price']:.2f}**")
    else:
        st.info("No active crossover signals match the criteria in the selected timeframe.")
