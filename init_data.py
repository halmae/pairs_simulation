import os
import ccxt
import pandas as pd
from datetime import datetime
import time
from tqdm import tqdm

def create_crypto_data_structure(start_date, end_date):
    """
    암호화폐 데이터 구조를 생성하고 데이터를 다운로드하는 함수
    
    Parameters:
    start_date (str): 시작 날짜 (YYYY-MM-DD)
    end_date (str): 종료 날짜 (YYYY-MM-DD)
    """
    # 기본 설정
    base_dir = 'data'
    symbols = ['BTC', 'ETH', 'SOL']
    timeframes = ['1d', '1h', '1m', '5m']
    
    # 1. data 폴더 생성
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        print(f"Created directory: {base_dir}")
    
    # 각 심볼에 대해 처리
    for symbol in tqdm(symbols, desc="Processing symbols"):
        symbol_dir = f"{base_dir}/{symbol}USDT"
        
        # 2. 심볼별 폴더 생성
        if not os.path.exists(symbol_dir):
            os.makedirs(symbol_dir)
            print(f"Created directory: {symbol_dir}")
        
        # 3. 각 timeframe별 데이터 다운로드 및 저장
        for timeframe in tqdm(timeframes, desc=f"Downloading {symbol} data", leave=False):
            filename = f"{symbol}USDT_{timeframe}_{start_date}_to_{end_date}.csv"
            filepath = f"{symbol_dir}/{filename}"
            
            # 이미 존재하는 파일 건너뛰기
            if os.path.exists(filepath):
                print(f"File already exists: {filepath}")
                continue
            
            try:
                # OHLCV 데이터 가져오기
                exchange = ccxt.binance()
                df = fetch_ohlcv(f"{symbol}/USDT", timeframe, start_date, end_date)
                
                if df is not None and not df.empty:
                    # CSV 파일로 저장
                    df.to_csv(filepath, index=False)
                    print(f"Saved: {filepath}")
                    
                    # API 호출 제한 방지
                    time.sleep(1)
                
            except Exception as e:
                print(f"Error downloading {symbol} {timeframe}: {str(e)}")
                continue

def fetch_ohlcv(symbol, timeframe, start_date, end_date):
    """
    OHLCV 데이터를 가져오는 함수 (이전에 정의한 함수 사용)
    """
    exchange = ccxt.binance()
    
    # 날짜를 timestamp로 변환
    start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
    end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)
    
    try:
        all_ohlcv = []
        current_timestamp = start_timestamp
        
        while current_timestamp < end_timestamp:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=current_timestamp, limit=1000)
            if len(ohlcv) == 0:
                break
                
            all_ohlcv.extend(ohlcv)
            current_timestamp = ohlcv[-1][0] + 1
            time.sleep(1)
        
        if all_ohlcv:
            df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        
        return None
    
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None

# 사용 예시:
if __name__ == "__main__":
    start_date = "2023-01-01"
    end_date = "2024-11-30"
    create_crypto_data_structure(start_date, end_date)