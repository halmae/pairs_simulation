import numpy as np
import pandas as pd

def generate_signals(test_window, target_window, alpha=1.0):
    """
    1: long spread (long coin1, short coin2)
    -1: short spread (short coin1, long coin2)
    0: close position
    """
    
    mean = test_window.mean()
    std = test_window.std()
    
    upper_bound = mean + std * alpha
    lower_bound = mean - std * alpha
    
    signals = np.zeros(len(target_window))
    position = 0
    
    for i in range(len(target_window)):
        current_price = target_window.iloc[i]
        
        if position == 0:
            if current_price < lower_bound:
                signals[i] = 1
                position = 1
            elif current_price > upper_bound:
                signals[i] = -1
                position = -1
        
        elif position == 1:
            if current_price > mean:
                signals[i] = 0
                position = 0
        
        elif position == -1:
            if current_price < mean:
                signals[i] = 0
                position = 0
        
    return signals

def backtest_strategy(coin1_prices, coin2_prices, signals):
    returns = pd.Series(0.0, index=signals.index)
    position = 0
    entry_coin1_price = 0
    entry_coin2_price = 0
    
    for i in range(1, len(signals)):
        current_signal = signals[i]
        
        if position == 0 and current_signal != 0:
            position = current_signal
            entry_coin1_price = coin1_prices[i]
            entry_coin2_price = coin2_prices[i]
            
        elif position != 0 and current_signal == 0:    
            if position == 1:
                returns[i] = (coin1_prices[i]/entry_coin1_price) - (coin2_prices[i]/entry_coin2_price)
            else:
                returns[i] = (coin2_prices[i]/entry_coin2_price) - (coin1_prices[i]/entry_coin1_price)
            
            position = 0
            entry_coin1_price =0
            entry_coin2_price = 0
        
    cumulative_returns = (1 + returns).cumprod() - 1
    
    return cumulative_returns, signals
    
    
