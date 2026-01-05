"""
Collect and store stock market data
"""
import sys
import os
import time
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app import crud, schemas
from app.services.data_collector import fetch_stock_data, get_all_companies
from app.services.data_processor import clean_and_process_data, prepare_data_for_db, calculate_52_week_high_low
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def collect_stock_data(symbol: str, period: str = "1y", use_mock_fallback: bool = True):
    """Collect and store data for a single stock"""
    db = SessionLocal()
    try:
        logger.info(f"Fetching data for {symbol}...")
        
        # Fetch data
        df = fetch_stock_data(symbol, period=period, use_mock_fallback=use_mock_fallback)
        
        if df is None or df.empty:
            logger.warning(f"No data fetched for {symbol}")
            return False
        
        # Process data
        df = clean_and_process_data(df)
        
        if df.empty:
            logger.warning(f"No data after processing for {symbol}")
            return False
        
        # Prepare for database
        records = prepare_data_for_db(df, symbol)
        
        if not records:
            logger.warning(f"No records to insert for {symbol}")
            return False
        
        # Insert data
        inserted_count = 0
        for record in records:
            try:
                stock_data = schemas.StockDataBase(**record)
                crud.create_stock_data(db, stock_data)
                inserted_count += 1
            except Exception as e:
                logger.debug(f"Error inserting record: {str(e)}")
                continue
        
        logger.info(f"Inserted {inserted_count} records for {symbol}")
        
        # Calculate and store summary
        summary_data = calculate_52_week_high_low(df)
        current_price = float(df['close'].iloc[-1]) if not df.empty else None
        
        summary = schemas.StockSummaryBase(
            symbol=symbol,
            week_52_high=summary_data["week_52_high"],
            week_52_low=summary_data["week_52_low"],
            avg_close=summary_data["avg_close"],
            current_price=current_price
        )
        
        crud.create_or_update_stock_summary(db, summary)
        logger.info(f"Updated summary for {symbol}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error collecting data for {symbol}: {str(e)}")
        return False
    finally:
        db.close()

def collect_all_data(period: str = "1y", use_mock_fallback: bool = True):
    """Collect data for all companies"""
    companies = get_all_companies()
    logger.info(f"Collecting data for {len(companies)} companies...")
    if use_mock_fallback:
        logger.info("Note: Mock data will be used as fallback if yfinance fails")
    
    success_count = 0
    for i, company in enumerate(companies, 1):
        symbol = company["symbol"]
        logger.info(f"[{i}/{len(companies)}] Processing {symbol}...")
        
        if collect_stock_data(symbol, period=period, use_mock_fallback=use_mock_fallback):
            success_count += 1
        
        # Add delay between requests to avoid rate limiting
        if i < len(companies):
            time.sleep(1)  # 1 second delay between requests
    
    logger.info(f"Data collection complete! Successfully collected data for {success_count}/{len(companies)} companies")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Collect stock market data")
    parser.add_argument(
        "--symbol",
        type=str,
        help="Collect data for a specific symbol (e.g., RELIANCE.NS)"
    )
    parser.add_argument(
        "--period",
        type=str,
        default="1y",
        help="Period to fetch (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Collect data for all companies"
    )
    parser.add_argument(
        "--no-mock",
        action="store_true",
        help="Disable mock data fallback (will fail if yfinance fails)"
    )
    
    args = parser.parse_args()
    
    use_mock = not args.no_mock
    
    if args.symbol:
        collect_stock_data(args.symbol, period=args.period, use_mock_fallback=use_mock)
    elif args.all:
        collect_all_data(period=args.period, use_mock_fallback=use_mock)
    else:
        logger.info("Collecting data for all companies (default)...")
        collect_all_data(period=args.period, use_mock_fallback=use_mock)

