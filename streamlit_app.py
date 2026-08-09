import pandas as pd
import numpy as np

def generate_signals(df):
    # 1. Trend Basis (Fast & Slow EMA)
    df['EMA_Fast'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA_Slow'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    # 2. Momentum proxy (MACD Histogram simplification)
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=9, adjust=False).mean()
    macd_hist = macd - signal_line
    
    # 3. Conditions
    trend_up = df['EMA_Fast'] > df['EMA_Slow']
    trend_dn = df['EMA_Fast'] < df['EMA_Slow']
    momentum_up = macd_hist > 0
    momentum_dn = macd_hist < 0
    
    # Crossover logic
    crossover = (df['EMA_Fast'] > df['EMA_Slow']) & (df['EMA_Fast'].shift(1) <= df['EMA_Slow'].shift(1))
    crossunder = (df['EMA_Fast'] < df['EMA_Slow']) & (df['EMA_Fast'].shift(1) >= df['EMA_Slow'].shift(1))
    
    df['Buy_Signal'] = crossover & trend_up & momentum_up
    df['Sell_Signal'] = crossunder & trend_dn & momentum_dn
    
    return df
