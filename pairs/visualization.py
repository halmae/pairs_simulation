import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from utility_functions import *
from signals import *


def run_strategy_for_period(coin1_prices, coin2_prices, window_size):
    """
    특정 기간에 대한 전략 실행
    """
    spread = np.log(coin1_prices) - np.log(coin2_prices)
    windows = rolling_window_pairs(spread, window_size)
    
    all_signals = []
    for w in windows:
        signals = generate_signals(w['test_window'], w['target_window'])
        all_signals.extend(signals)
    
    if len(all_signals) > 0:
        all_signals = pd.Series(all_signals, index=spread.index[window_size:len(all_signals)+window_size])
        returns, positions = backtest_strategy(coin1_prices[all_signals.index], 
                                            coin2_prices[all_signals.index], 
                                            all_signals)
        return returns, positions
    return pd.Series(), pd.Series()


def plot_all_periods_returns(backtest_returns, insample_returns, outsample_returns, 
                           pair_name, window_size):
    plt.style.use('seaborn-v0_8')
    fig, ax = plt.subplots(figsize=(15, 7))
    
    # 각 기간 플로팅
    backtest_returns.plot(ax=ax, color='blue', linewidth=1.5, label='Backtest Period')
    insample_returns.plot(ax=ax, color='green', linewidth=1.5, label='In-Sample Period')
    outsample_returns.plot(ax=ax, color='red', linewidth=1.5, label='Out-Sample Period')
    
    # 그래프 꾸미기
    ax.set_title(f'Cumulative Returns for {pair_name}\n(Window Size: {window_size})', 
                fontsize=12, pad=15)
    ax.set_xlabel('Date')
    ax.set_ylabel('Cumulative Returns (%)')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Y축 퍼센트로 표시
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.1%}'.format(y)))
    
    # 각 기간별 성과 통계 계산
    backtest_metrics = calculate_performance_metrics(backtest_returns)
    insample_metrics = calculate_performance_metrics(insample_returns)
    outsample_metrics = calculate_performance_metrics(outsample_returns)
    
    # 성과 통계 표시
    # stats_text = (
    #     f'Backtest Period:\n'
    #     f'  Return: {backtest_metrics["Total Return (%)"]}%\n'
    #     f'  Sharpe: {backtest_metrics["Sharpe Ratio"]}\n'
    #     f'  Sortino: {backtest_metrics["Sortino Ratio"]}\n\n'
    #     f'In-Sample Period:\n'
    #     f'  Return: {insample_metrics["Total Return (%)"]}%\n'
    #     f'  Sharpe: {insample_metrics["Sharpe Ratio"]}\n'
    #     f'  Sortino: {insample_metrics["Sortino Ratio"]}\n\n'
    #     f'Out-Sample Period:\n'
    #     f'  Return: {outsample_metrics["Total Return (%)"]}%\n'
    #     f'  Sharpe: {outsample_metrics["Sharpe Ratio"]}\n'
    #     f'  Sortino: {outsample_metrics["Sortino Ratio"]}'
    # )
    # plt.figtext(0.15, 0.95, stats_text, fontsize=10, ha='left', va='top')
    
    plt.tight_layout()
    return fig, {
        'Backtest': backtest_metrics,
        'In-Sample': insample_metrics,
        'Out-Sample': outsample_metrics
    }

def visualize_all_periods(coin1, coin2, tf='1d', window_size=30):
    backtest_data, insample_data, outsample_data = split_data_periods(tf)
    
    # 각 기간별 전략 실행
    backtest_returns, _ = run_strategy_for_period(
        backtest_data[coin1]['Close'], backtest_data[coin2]['Close'], window_size)
    
    insample_returns, _ = run_strategy_for_period(
        insample_data[coin1]['Close'], insample_data[coin2]['Close'], window_size)
    
    outsample_returns, _ = run_strategy_for_period(
        outsample_data[coin1]['Close'], outsample_data[coin2]['Close'], window_size)
    
    # 시각화 및 성과 분석
    pair_name = f'{coin1}-{coin2}'
    fig, metrics = plot_all_periods_returns(backtest_returns, insample_returns, outsample_returns,
                                          pair_name, window_size)
    plt.show()
    
    return backtest_returns, insample_returns, outsample_returns, metrics