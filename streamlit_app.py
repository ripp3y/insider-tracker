import json
import os
import pandas as pd
import streamlit as st
import yfinance as yf

st.title("📈 Algorithmic Signal Tracker + Watchlist")

# --- WATCHLIST STORAGE LOGIC ---
WATCHLIST_FILE = "watchlist.json"

def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        try:
            with open(WATCHLIST_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    # Default fallback list based on your portfolio
    return ["COHR", "AXTI", "WOLF", "RKLB", "LUNR", "ENVA", "ALB"]

def save_watchlist(watchlist):
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(watchlist, f)

# Initialize session state for watchlist
if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_watchlist()

# --- SIDEBAR WATCHLIST MANAGEMENT ---
st.sidebar.header("📁 Cloud Watchlist")

new_ticker = st.sidebar.text_input("Add Ticker to Watchlist").upper()
if st.sidebar.button("Add Ticker"):
    if new_ticker and new_ticker not in st.session_state.watchlist:
        st.session_state.watchlist.append(new_ticker)
        save_watchlist(st.session_state.watchlist)
        st.sidebar.success(f"Added {new_ticker}!")
        st.rerun()

# Allow selecting from the saved watchlist or typing manually
selected_ticker = st.sidebar.selectbox("Select from Watchlist", st.session_state.watchlist)

# Option to remove a ticker
if st.sidebar.button("Remove Selected Ticker"):
    if selected_ticker in st.session_state.watchlist:
        st.session_state.watchlist.remove(selected_ticker)
        save_watchlist(st.session_state.watchlist)
        st.sidebar.warning(f"Removed {selected_ticker}!")
        st.rerun()

# Main input fallback
ticker_symbol = st.text_input("Or Enter Any Ticker Symbol", value=selected_ticker).upper()

@st.cache_data
def calculate_custom_strategy(ticker, period="6mo"):
    df = yf.download(ticker, period=period, interval="1d")
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    df['EMA_Fast'] = df['Close'].ewm(span=5, adjust=False).mean()
    df['EMA_Slow'] = df['Close'].ewm(span=13, adjust=False).mean()
    
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = macd - signal_line
    
    trend_up = df['EMA_Fast'] > df['EMA_Slow']
    trend_dn = df['EMA_Fast'] < df['EMA_Slow']
    momentum_up = df['MACD_Hist'] > 0
    momentum_dn = df['MACD_Hist'] < 0
    
    crossover = (df['EMA_Fast'] > df['EMA_Slow']) & (df['EMA_Fast'].shift(1) <= df['EMA_Slow'].shift(1))
    crossunder = (df['EMA_Fast'] < df['EMA_Slow']) & (df['EMA_Fast'].shift(1) >= df['EMA_Slow'].shift(1))
    
    df['Signal'] = "HOLD"
    df.loc[crossover & trend_up & momentum_up, 'Signal'] = "BUY"
    df.loc[crossunder & trend_dn & momentum_dn, 'Signal'] = "SELL"
    
    if ticker.upper() in ["WOLF", "AXTI"]:
        trailing_pct = 0.08
    else:
        trailing_pct = 0.05
        
    df['Running_Max'] = df['Close'].cummax()
    df['Trailing_Stop_Price'] = df['Running_Max'] * (1 - trailing_pct)
    
    return df

if ticker_symbol:
    data = calculate_custom_strategy(ticker_symbol)
    
    st.line_chart(data[['Close', 'EMA_Fast', 'EMA_Slow']])

    signal_history = data[data['Signal'] != "HOLD"]

    st.subheader(f"🎯 Triggered Signals & Stop Targets: {ticker_symbol}")

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
