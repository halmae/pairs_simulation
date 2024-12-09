import numpy as np
import pandas as pd


def split_data_periods(tf):
    root = '../data/'
    dates = '2023-01-01_to_2024-11-30'
    coins = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
    timeframes = ['1m', '5m', '1h', '1d']
    
    if tf not in timeframes:
        raise ValueError(f"Timeframe '{tf}' is not valid. Please use one of: '1m', '5m', '1h', '1d'")
    
    backtest_start = '2023-01-01'
    backtest_end = '2024-05-31'
    insample_start = '2024-06-01'
    insample_end = '2024-09-30'
    outsample_start = '2024-10-01'
    outsample_end = '2024-11-30'
    
    if tf == '1m':
        btc = pd.read_csv(root + f'{coins[0]}/{coins[0]}_{timeframes[0]}_{dates}.csv', index_col=0, parse_dates=True)
        eth = pd.read_csv(root + f'{coins[1]}/{coins[1]}_{timeframes[0]}_{dates}.csv', index_col=0, parse_dates=True)
        sol = pd.read_csv(root + f'{coins[2]}/{coins[2]}_{timeframes[0]}_{dates}.csv', index_col=0, parse_dates=True)
    elif tf == '5m':
        btc = pd.read_csv(root + f'{coins[0]}/{coins[0]}_{timeframes[1]}_{dates}.csv', index_col=0, parse_dates=True)
        eth = pd.read_csv(root + f'{coins[1]}/{coins[1]}_{timeframes[1]}_{dates}.csv', index_col=0, parse_dates=True)
        sol = pd.read_csv(root + f'{coins[2]}/{coins[2]}_{timeframes[1]}_{dates}.csv', index_col=0, parse_dates=True)
    elif tf == '1h':
        btc = pd.read_csv(root + f'{coins[0]}/{coins[0]}_{timeframes[2]}_{dates}.csv', index_col=0, parse_dates=True)
        eth = pd.read_csv(root + f'{coins[1]}/{coins[1]}_{timeframes[2]}_{dates}.csv', index_col=0, parse_dates=True)
        sol = pd.read_csv(root + f'{coins[2]}/{coins[2]}_{timeframes[2]}_{dates}.csv', index_col=0, parse_dates=True)
    elif tf == '1d':
        btc = pd.read_csv(root + f'{coins[0]}/{coins[0]}_{timeframes[3]}_{dates}.csv', index_col=0, parse_dates=True)
        eth = pd.read_csv(root + f'{coins[1]}/{coins[1]}_{timeframes[3]}_{dates}.csv', index_col=0, parse_dates=True)
        sol = pd.read_csv(root + f'{coins[2]}/{coins[2]}_{timeframes[3]}_{dates}.csv', index_col=0, parse_dates=True)


    backtest_data = {
        'BTC': btc.loc[backtest_start:backtest_end],
        'ETH': eth.loc[backtest_start:backtest_end],
        'SOL': sol.loc[backtest_start:backtest_end]
    }

    insample_data = {
        'BTC': btc.loc[insample_start:insample_end],
        'ETH': eth.loc[insample_start:insample_end],
        'SOL': sol.loc[insample_start:insample_end]
    }

    outsample_data = {
        'BTC': btc.loc[outsample_start:outsample_end],
        'ETH': eth.loc[outsample_start:outsample_end],
        'SOL': sol.loc[outsample_start:outsample_end]
    }

    return backtest_data, insample_data, outsample_data


def rolling_window_pairs(data, window_size):
    total_length = len(data)
    n_windows = (total_length - window_size) // window_size
    
    windows = []
    
    for i in range(n_windows):
        start_test = i * window_size
        end_test = start_test + window_size
        start_target = end_test
        end_target = start_target + window_size
        
        if end_target > total_length:
            break
        
        test_window = data[start_test:end_test]
        target_window = data[start_target:end_target]
        
        windows.append({
            'test_window': test_window,
            'target_window': target_window,
            'test_period': (data.index[start_test], data.index[end_test-1]),
            'target_period': (data.index[start_target], data.index[end_target-1])
        })
    
    return windows


def calculate_performance_metrics(returns, risk_free_rate=0.02):
    """
    각 기간별 성과 지표 계산
    """
    if len(returns) == 0:
        return {
            'Total Return (%)': 0.0,
            'Annualized Return (%)': 0.0,
            'Sharpe Ratio': 0.0,
            'Sortino Ratio': 0.0,
            'Max Drawdown (%)': 0.0
        }
    
    # 일별 수익률 계산
    daily_returns = returns.pct_change().dropna()
    
    if len(daily_returns) == 0:
        return {
            'Total Return (%)': 0.0,
            'Annualized Return (%)': 0.0,
            'Sharpe Ratio': 0.0,
            'Sortino Ratio': 0.0,
            'Max Drawdown (%)': 0.0
        }
    
    # 연율화 계수
    trading_days = 252
    annual_factor = np.sqrt(trading_days)
    
    # 총 수익률
    total_return = returns.iloc[-1] - returns.iloc[0]
    
    # 연율화 수익률
    period_days = (returns.index[-1] - returns.index[0]).days
    if period_days > 0:
        years = period_days / 365
        annualized_return = (1 + total_return) ** (1/years) - 1
    else:
        annualized_return = total_return
    
    # 변동성 계산
    vol = daily_returns.std() * annual_factor
    
    # 하방 변동성 계산
    downside_returns = daily_returns[daily_returns < 0]
    downside_vol = downside_returns.std() * annual_factor if len(downside_returns) > 0 else vol
    
    # Sharpe ratio
    excess_return = annualized_return - risk_free_rate
    sharpe = excess_return / vol if vol != 0 else 0
    
    # Sortino ratio
    sortino = excess_return / downside_vol if downside_vol != 0 else 0
    
    # Maximum Drawdown
    cummax = returns.cummax()
    drawdown = (cummax - returns) / cummax
    max_drawdown = drawdown.max()
    
    return {
        'Total Return (%)': round(total_return * 100, 2),
        'Annualized Return (%)': round(annualized_return * 100, 2),
        'Sharpe Ratio': round(sharpe, 2),
        'Sortino Ratio': round(sortino, 2),
        'Max Drawdown (%)': round(max_drawdown * 100, 2)
    }
    