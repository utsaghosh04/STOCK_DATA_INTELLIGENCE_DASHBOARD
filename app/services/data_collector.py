import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from typing import List, Optional
import logging
import time
import random

logging.getLogger("yfinance").setLevel(logging.CRITICAL)


logger = logging.getLogger(__name__)

# Popular Indian stocks (NSE symbols with .NS suffix for yfinance)
INDIAN_STOCKS = [
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries", "exchange": "NSE", "sector": "Energy"},
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services", "exchange": "NSE", "sector": "Technology"},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank", "exchange": "NSE", "sector": "Financial"},
    {"symbol": "INFY.NS", "name": "Infosys", "exchange": "NSE", "sector": "Technology"},
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank", "exchange": "NSE", "sector": "Financial"},
    {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever", "exchange": "NSE", "sector": "Consumer Goods"},
    {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel", "exchange": "NSE", "sector": "Telecommunications"},
    {"symbol": "SBIN.NS", "name": "State Bank of India", "exchange": "NSE", "sector": "Financial"},
    {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance", "exchange": "NSE", "sector": "Financial"},
    {"symbol": "WIPRO.NS", "name": "Wipro", "exchange": "NSE", "sector": "Technology"},
    {"symbol": "ITC.NS", "name": "ITC Limited", "exchange": "NSE", "sector": "Consumer Goods"},
    {"symbol": "LT.NS", "name": "Larsen & Toubro", "exchange": "NSE", "sector": "Engineering"},
    {"symbol": "AXISBANK.NS", "name": "Axis Bank", "exchange": "NSE", "sector": "Financial"},
    {"symbol": "MARUTI.NS", "name": "Maruti Suzuki", "exchange": "NSE", "sector": "Automotive"},
    {"symbol": "TITAN.NS", "name": "Titan Company", "exchange": "NSE", "sector": "Retail"},
]

def generate_mock_data(symbol: str, days: int = 365) -> pd.DataFrame:
    """
    Generate mock stock data as fallback when yfinance fails
    Creates realistic-looking stock price data with trends and volatility
    """
    logger.info(f"Generating mock data for {symbol} (fallback mode)")
    
    # Base price varies by symbol (for realism)
    base_prices = {
        "RELIANCE.NS": 2500,
        "TCS.NS": 3500,
        "HDFCBANK.NS": 1600,
        "INFY.NS": 1500,
        "ICICIBANK.NS": 900,
        "HINDUNILVR.NS": 2400,
        "BHARTIARTL.NS": 1100,
        "SBIN.NS": 600,
        "BAJFINANCE.NS": 7000,
        "WIPRO.NS": 400,
        "ITC.NS": 450,
        "LT.NS": 3200,
        "AXISBANK.NS": 1000,
        "MARUTI.NS": 9500,
        "TITAN.NS": 3200,
    }
    
    base_price = base_prices.get(symbol, 1000)
    
    # Generate dates
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    # Filter to business days only (Monday-Friday)
    dates = dates[dates.weekday < 5]
    
    n_days = len(dates)
    
    # Generate price series with random walk and trend
    np.random.seed(hash(symbol) % 2**32)  # Deterministic seed based on symbol
    
    # Random walk with drift
    returns = np.random.normal(0.0005, 0.02, n_days)  # Small positive drift, 2% volatility
    prices = base_price * np.exp(np.cumsum(returns))
    
    # Generate OHLC data
    data = []
    for i, (dt, close) in enumerate(zip(dates, prices)):
        # Daily volatility
        daily_vol = np.random.uniform(0.01, 0.03)
        
        # Generate open (slight variation from previous close)
        if i == 0:
            open_price = close * np.random.uniform(0.98, 1.02)
        else:
            open_price = prices[i-1] * np.random.uniform(0.99, 1.01)
        
        # Generate high and low
        high = max(open_price, close) * (1 + np.random.uniform(0, daily_vol))
        low = min(open_price, close) * (1 - np.random.uniform(0, daily_vol))
        
        # Ensure high >= max(open, close) and low <= min(open, close)
        high = max(high, open_price, close)
        low = min(low, open_price, close)
        
        # Generate volume (higher volume on volatile days)
        volatility = abs(close - open_price) / open_price
        base_volume = np.random.uniform(1000000, 5000000)
        volume = int(base_volume * (1 + volatility * 2))
        
        data.append({
            'date': dt.date(),
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    return df

def fetch_stock_data(
    symbol: str, 
    period: str = "1y",
    interval: str = "1d",
    use_mock_fallback: bool = True
) -> Optional[pd.DataFrame]:

    max_retries = 2
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            if attempt > 0:
                time.sleep(retry_delay)

            # ✅ USE download instead of Ticker().history()
            data = yf.download(
                symbol,
                period=period,
                interval=interval,
                threads=False,       # CRITICAL
                auto_adjust=False,
                progress=False
            )

            # Hard fail if Yahoo returns junk
            if data is None or data.empty:
                raise ValueError("Empty dataframe from yfinance")

            # Handle MultiIndex columns (yf.download can return MultiIndex)
            if isinstance(data.columns, pd.MultiIndex):
                # Flatten MultiIndex columns
                data.columns = [col[0].lower() if isinstance(col, tuple) else str(col).lower() 
                               for col in data.columns]
            else:
                # Normalize columns
                data.columns = [str(c).lower() for c in data.columns]

            # Ensure we have the required columns
            required_cols = {"open", "high", "low", "close", "volume"}
            available_cols = set(data.columns)
            if not required_cols.issubset(available_cols):
                # Try to find columns with different casing or names
                col_mapping = {}
                for req_col in required_cols:
                    for avail_col in available_cols:
                        if req_col in str(avail_col).lower():
                            col_mapping[req_col] = avail_col
                            break
                
                if len(col_mapping) < len(required_cols):
                    raise ValueError(f"Missing required columns. Available: {available_cols}, Required: {required_cols}")
                
                # Rename columns to standard names
                data.rename(columns=col_mapping, inplace=True)

            data.reset_index(inplace=True)

            # Handle Date / Datetime index safely
            if "date" in data.columns:
                data["date"] = pd.to_datetime(data["date"]).dt.date
            elif "datetime" in data.columns:
                data.rename(columns={"datetime": "date"}, inplace=True)
                data["date"] = pd.to_datetime(data["date"]).dt.date

            logger.info(f"Successfully fetched {len(data)} records for {symbol}")
            return data

        except Exception as e:
            if attempt == 0:
                logger.warning(
                    f"Error fetching data for {symbol}, retrying once: {str(e)[:100]}"
                )
            else:
                logger.warning(
                    f"Error fetching data for {symbol} after {attempt + 1} attempts: {str(e)[:100]}"
                )

    # -------------------------
    # Mock fallback
    # -------------------------
    logger.warning(f"yfinance failed for {symbol}, using mock data fallback")

    if use_mock_fallback:
        logger.info(f"Generating mock data for {symbol}")
        return generate_mock_data(
            symbol,
            days=365 if period == "1y" else 30
        )

    return None

def get_company_info(symbol: str) -> Optional[dict]:
    """Get company information"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            "symbol": symbol,
            "name": info.get("longName", symbol),
            "exchange": info.get("exchange", "NSE"),
            "sector": info.get("sector", "Unknown")
        }
    except Exception as e:
        logger.error(f"Error fetching company info for {symbol}: {str(e)}")
        return None

def get_all_companies() -> List[dict]:
    """Get list of all companies we track"""
    return INDIAN_STOCKS

