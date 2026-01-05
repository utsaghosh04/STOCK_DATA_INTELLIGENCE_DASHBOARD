from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta
from app import crud, schemas
from app.database import get_db
from app.services.data_processor import calculate_correlation
from app.cache import cache
import pandas as pd

router = APIRouter(prefix="/data", tags=["data"])

# IMPORTANT: More specific routes must be defined before parameterized routes
# Order matters in FastAPI!

@router.get("/compare", response_model=schemas.ComparisonResponse)
async def compare_stocks(
    symbol1: str = Query(..., description="First stock symbol"),
    symbol2: str = Query(..., description="Second stock symbol"),
    days: int = Query(30, ge=1, le=365, description="Number of days to compare"),
    db: Session = Depends(get_db)
):
    """Compare two stocks' performance"""
    # Check cache
    cached = cache.get("compare", symbol1=symbol1, symbol2=symbol2, days=days)
    if cached is not None:
        return cached
    
    # Get data for both symbols
    data1 = crud.get_stock_data(db, symbol=symbol1, days=days)
    data2 = crud.get_stock_data(db, symbol=symbol2, days=days)
    
    if not data1:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol1}")
    if not data2:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol2}")
    
    # Convert to DataFrames for correlation calculation
    df1 = pd.DataFrame([{
        'date': d.date,
        'close': d.close
    } for d in data1])
    
    df2 = pd.DataFrame([{
        'date': d.date,
        'close': d.close
    } for d in data2])
    
    # Calculate correlation
    correlation = calculate_correlation(df1, df2)
    
    # Get summaries
    summary1 = crud.get_stock_summary(db, symbol=symbol1)
    summary2 = crud.get_stock_summary(db, symbol=symbol2)
    
    if not summary1:
        raise HTTPException(status_code=404, detail=f"No summary found for {symbol1}")
    if not summary2:
        raise HTTPException(status_code=404, detail=f"No summary found for {symbol2}")
    
    result = schemas.ComparisonResponse(
        symbol1=symbol1,
        symbol2=symbol2,
        correlation=correlation,
        symbol1_data=data1,
        symbol2_data=data2,
        symbol1_summary=summary1,
        symbol2_summary=summary2
    )
    
    # Cache for 5 minutes
    cache.set("compare", result, ttl=300, symbol1=symbol1, symbol2=symbol2, days=days)
    return result

@router.get("/summary/{symbol}", response_model=schemas.StockSummary)
async def get_stock_summary(symbol: str, db: Session = Depends(get_db)):
    """Get 52-week high, low, and average close for a symbol"""
    # Check cache
    cached = cache.get("stock_summary", symbol=symbol)
    if cached is not None:
        return cached
    
    summary = crud.get_stock_summary(db, symbol=symbol)
    if summary is None:
        raise HTTPException(
            status_code=404,
            detail=f"No summary found for symbol {symbol}"
        )
    
    # Cache for 10 minutes
    cache.set("stock_summary", summary, ttl=600, symbol=symbol)
    return summary

@router.get("/{symbol}", response_model=List[schemas.StockData])
async def get_stock_data(
    symbol: str,
    days: int = Query(30, ge=1, le=365, description="Number of days of data"),
    db: Session = Depends(get_db)
):
    """Get stock data for a symbol (last N days)"""
    # Check cache
    cached = cache.get("stock_data", symbol=symbol, days=days)
    if cached is not None:
        return cached
    
    stock_data = crud.get_stock_data(db, symbol=symbol, days=days)
    if not stock_data:
        raise HTTPException(
            status_code=404, 
            detail=f"No data found for symbol {symbol}"
        )
    
    # Cache for 5 minutes
    cache.set("stock_data", stock_data, ttl=300, symbol=symbol, days=days)
    return stock_data
