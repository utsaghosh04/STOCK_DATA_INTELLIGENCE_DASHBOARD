from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import date, datetime, timedelta
from typing import List, Optional
from app import models, schemas

def get_company(db: Session, symbol: str):
    """Get a company by symbol"""
    return db.query(models.Company).filter(models.Company.symbol == symbol).first()

def get_companies(db: Session, skip: int = 0, limit: int = 100):
    """Get all companies"""
    return db.query(models.Company).offset(skip).limit(limit).all()

def create_company(db: Session, company: schemas.CompanyBase):
    """Create a new company"""
    db_company = models.Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def get_stock_data(
    db: Session, 
    symbol: str, 
    days: int = 30,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get stock data for a symbol"""
    query = db.query(models.StockData).filter(models.StockData.symbol == symbol)
    
    if start_date:
        query = query.filter(models.StockData.date >= start_date)
    if end_date:
        query = query.filter(models.StockData.date <= end_date)
    if not start_date and not end_date:
        # Default to last N days
        cutoff_date = date.today() - timedelta(days=days)
        query = query.filter(models.StockData.date >= cutoff_date)
    
    return query.order_by(models.StockData.date.desc()).all()

def create_stock_data(db: Session, stock_data: schemas.StockDataBase):
    """Create or update stock data"""
    existing = db.query(models.StockData).filter(
        models.StockData.symbol == stock_data.symbol,
        models.StockData.date == stock_data.date
    ).first()
    
    if existing:
        # Update existing record
        for key, value in stock_data.dict().items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new record
        db_stock_data = models.StockData(**stock_data.dict())
        db.add(db_stock_data)
        db.commit()
        db.refresh(db_stock_data)
        return db_stock_data

def bulk_create_stock_data(db: Session, stock_data_list: List[schemas.StockDataBase]):
    """Bulk create stock data"""
    db_objects = [models.StockData(**data.dict()) for data in stock_data_list]
    db.bulk_insert_mappings(
        models.StockData,
        [obj.__dict__ for obj in db_objects]
    )
    db.commit()
    return len(db_objects)

def get_stock_summary(db: Session, symbol: str):
    """Get stock summary for a symbol"""
    return db.query(models.StockSummary).filter(models.StockSummary.symbol == symbol).first()

def create_or_update_stock_summary(db: Session, summary: schemas.StockSummaryBase):
    """Create or update stock summary"""
    existing = db.query(models.StockSummary).filter(
        models.StockSummary.symbol == summary.symbol
    ).first()
    
    if existing:
        for key, value in summary.dict().items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        db_summary = models.StockSummary(**summary.dict())
        db.add(db_summary)
        db.commit()
        db.refresh(db_summary)
        return db_summary

def get_top_gainers_losers(db: Session, limit: int = 10):
    """Get top gainers and losers based on daily return"""
    # Get most recent date for each symbol
    subquery = db.query(
        models.StockData.symbol,
        func.max(models.StockData.date).label('max_date')
    ).group_by(models.StockData.symbol).subquery()
    
    # Get latest data with daily return
    latest_data = db.query(models.StockData).join(
        subquery,
        (models.StockData.symbol == subquery.c.symbol) &
        (models.StockData.date == subquery.c.max_date)
    ).filter(models.StockData.daily_return.isnot(None)).all()
    
    # Sort by daily return
    sorted_data = sorted(latest_data, key=lambda x: x.daily_return or 0, reverse=True)
    
    gainers = sorted_data[:limit]
    losers = sorted_data[-limit:] if len(sorted_data) >= limit else sorted_data
    losers.reverse()  # Show worst first
    
    return gainers, losers

def get_most_volatile(db: Session, limit: int = 10):
    """Get most volatile stocks based on volatility score"""
    subquery = db.query(
        models.StockData.symbol,
        func.max(models.StockData.date).label('max_date')
    ).group_by(models.StockData.symbol).subquery()
    
    latest_data = db.query(models.StockData).join(
        subquery,
        (models.StockData.symbol == subquery.c.symbol) &
        (models.StockData.date == subquery.c.max_date)
    ).filter(models.StockData.volatility_score.isnot(None)).all()
    
    sorted_data = sorted(
        latest_data, 
        key=lambda x: x.volatility_score or 0, 
        reverse=True
    )
    
    return sorted_data[:limit]

