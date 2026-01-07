from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app import crud, schemas
from app.database import get_db
from app.services.ml_predictor import get_predictor
from app.cache import cache
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/insights", tags=["insights"])

@router.get("", response_model=schemas.InsightResponse)
async def get_insights(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get market insights: top gainers, losers, and most volatile stocks"""
    # Check cache
    cached = cache.get("insights", limit=limit)
    if cached is not None:
        return cached
    
    gainers, losers = crud.get_top_gainers_losers(db, limit=limit)
    volatile = crud.get_most_volatile(db, limit=limit)
    
    result = schemas.InsightResponse(
        top_gainers=[
            {
                "symbol": g.symbol,
                "daily_return": g.daily_return,
                "close": g.close,
                "date": g.date.isoformat()
            }
            for g in gainers
        ],
        top_losers=[
            {
                "symbol": l.symbol,
                "daily_return": l.daily_return,
                "close": l.close,
                "date": l.date.isoformat()
            }
            for l in losers
        ],
        most_volatile=[
            {
                "symbol": v.symbol,
                "volatility_score": v.volatility_score,
                "close": v.close,
                "date": v.date.isoformat()
            }
            for v in volatile
        ],
        last_updated=datetime.now()
    )
    
    # Cache for 2 minutes (insights change frequently)
    cache.set("insights", result, ttl=120, limit=limit)
    return result

@router.get("/predict/{symbol}", response_model=schemas.PredictionResponse)
async def predict_price(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get price prediction for a stock using ML"""
    # Check cache (predictions cached for 1 hour)
    cached = cache.get("prediction", symbol=symbol)
    if cached is not None:
        return cached
    
    # Get historical data
    stock_data = crud.get_stock_data(db, symbol=symbol, days=100)
    
    if not stock_data:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for symbol {symbol}"
        )
    
    # Convert to DataFrame
    import pandas as pd
    df = pd.DataFrame([{
        'date': d.date,
        'close': d.close,
        'open': d.open,
        'high': d.high,
        'low': d.low,
        'volume': d.volume
    } for d in stock_data])
    
    # Get prediction
    predictor = get_predictor()
    predicted_price, confidence = predictor.predict_with_confidence(df)
    
    if predicted_price is None:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate prediction"
        )
    
    # Get current price
    current_price = stock_data[0].close if stock_data else 0.0
    
    result = schemas.PredictionResponse(
        symbol=symbol,
        current_price=current_price,
        predicted_price=predicted_price,
        confidence=confidence,
        prediction_date=datetime.now().date()
    )
    
    # Cache for 1 hour (predictions don't change frequently)
    cache.set("prediction", result, ttl=3600, symbol=symbol)
    return result

@router.post("/init-db")
async def initialize_database(db: Session = Depends(get_db)):
    """Initialize database and seed companies (safe to call multiple times)"""
    try:
        from app.services.data_collector import get_all_companies
        from app import crud, schemas
        
        companies = get_all_companies()
        added_count = 0
        
        for company_data in companies:
            existing = crud.get_company(db, symbol=company_data["symbol"])
            if not existing:
                company = schemas.CompanyBase(**company_data)
                crud.create_company(db, company)
                added_count += 1
        
        return {
            "message": "Database initialized successfully",
            "companies_added": added_count,
            "total_companies": len(companies)
        }
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize database: {str(e)}")

@router.post("/collect-data")
async def trigger_data_collection(
    symbol: str = None,
    db: Session = Depends(get_db)
):
    """Trigger data collection for all companies or a specific symbol"""
    try:
        import subprocess
        import sys
        
        if symbol:
            # Collect data for specific symbol
            result = subprocess.run(
                [sys.executable, "scripts/collect_data.py", "--symbol", symbol],
                capture_output=True,
                text=True,
                timeout=300
            )
        else:
            # Collect data for all companies
            result = subprocess.run(
                [sys.executable, "scripts/collect_data.py", "--all"],
                capture_output=True,
                text=True,
                timeout=600
            )
        
        if result.returncode == 0:
            return {
                "message": "Data collection completed",
                "output": result.stdout
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Data collection failed: {result.stderr}"
            )
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=504,
            detail="Data collection timed out. This is normal for large datasets."
        )
    except Exception as e:
        logger.error(f"Error collecting data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to collect data: {str(e)}"
        )

