import pandas as pd
import numpy as np
from typing import List, Optional
from datetime import date
import logging

logger = logging.getLogger(__name__)

def calculate_daily_return(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate daily return: (CLOSE - OPEN) / OPEN"""
    if 'close' in df.columns and 'open' in df.columns:
        df['daily_return'] = ((df['close'] - df['open']) / df['open']) * 100
    return df

def calculate_moving_average(df: pd.DataFrame, window: int = 7) -> pd.DataFrame:
    """Calculate N-day moving average"""
    if 'close' in df.columns:
        df[f'moving_avg_{window}'] = df['close'].rolling(window=window, min_periods=1).mean()
    return df

def calculate_52_week_high_low(df: pd.DataFrame) -> dict:
    """Calculate 52-week high and low"""
    if df.empty or 'close' not in df.columns:
        return {"week_52_high": None, "week_52_low": None, "avg_close": None}
    
    # Get last 52 weeks (approximately 252 trading days)
    recent_data = df.tail(252) if len(df) > 252 else df
    
    return {
        "week_52_high": float(recent_data['high'].max()),
        "week_52_low": float(recent_data['low'].min()),
        "avg_close": float(recent_data['close'].mean())
    }

def calculate_volatility_score(df: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    """
    Calculate volatility score based on standard deviation of returns
    Higher score = more volatile
    """
    if 'daily_return' in df.columns:
        df['volatility_score'] = df['daily_return'].rolling(
            window=window, min_periods=1
        ).std().abs()
    else:
        df['volatility_score'] = 0.0
    return df

def calculate_sentiment_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mock sentiment index based on price action
    Positive sentiment: price increasing with volume
    Negative sentiment: price decreasing with volume
    """
    if 'close' in df.columns and 'volume' in df.columns:
        # Price change
        price_change = df['close'].pct_change().fillna(0)
        
        # Volume change (normalized)
        volume_change = df['volume'].pct_change().fillna(0)
        
        # Combined sentiment (simple heuristic)
        # Positive if price up with volume, negative if price down with volume
        sentiment = (price_change * 0.7) + (np.sign(price_change) * volume_change * 0.3)
        
        # Scale to -100 to 100
        df['sentiment_index'] = sentiment * 100
        
        # Smooth with moving average
        df['sentiment_index'] = df['sentiment_index'].rolling(window=5, min_periods=1).mean()
    else:
        df['sentiment_index'] = 0.0
    
    return df

def calculate_correlation(df1: pd.DataFrame, df2: pd.DataFrame) -> float:
    """
    Calculate correlation between two stocks' closing prices
    """
    if df1.empty or df2.empty:
        return 0.0
    
    # Merge on date
    merged = pd.merge(
        df1[['date', 'close']],
        df2[['date', 'close']],
        on='date',
        suffixes=('_1', '_2')
    )
    
    if len(merged) < 2:
        return 0.0
    
    correlation = merged['close_1'].corr(merged['close_2'])
    return float(correlation) if not pd.isna(correlation) else 0.0

def clean_and_process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and process stock data
    - Handle missing values
    - Convert date columns
    - Calculate all metrics
    """
    if df.empty:
        return df
    
    # Make a copy
    df = df.copy()
    
    # Ensure date is date type
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date']).dt.date
    
    # Handle missing values in OHLCV
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    for col in numeric_cols:
        if col in df.columns:
            # Forward fill, then backward fill
            df[col] = df[col].ffill().bfill()
            # If still NaN, fill with 0
            df[col] = df[col].fillna(0)
    
    # Remove rows where close is 0 (invalid data)
    df = df[df['close'] > 0]
    
    # Sort by date
    df = df.sort_values('date').reset_index(drop=True)
    
    # Calculate metrics
    df = calculate_daily_return(df)
    df = calculate_moving_average(df, window=7)
    df = calculate_volatility_score(df, window=30)
    df = calculate_sentiment_index(df)
    
    # Fill any remaining NaN values
    df = df.fillna(0)
    
    return df

def prepare_data_for_db(df: pd.DataFrame, symbol: str) -> List[dict]:
    """
    Prepare processed DataFrame for database insertion
    """
    if df.empty:
        return []
    
    records = []
    for _, row in df.iterrows():
        record = {
            "symbol": symbol,
            "date": row['date'] if isinstance(row['date'], date) else pd.to_datetime(row['date']).date(),
            "open": float(row['open']),
            "high": float(row['high']),
            "low": float(row['low']),
            "close": float(row['close']),
            "volume": int(row['volume']),
            "daily_return": float(row.get('daily_return', 0.0)),
            "moving_avg_7": float(row.get('moving_avg_7', 0.0)),
            "volatility_score": float(row.get('volatility_score', 0.0)),
            "sentiment_index": float(row.get('sentiment_index', 0.0)),
        }
        records.append(record)
    
    return records

