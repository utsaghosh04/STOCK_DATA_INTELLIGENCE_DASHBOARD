from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db
from app.cache import cache

router = APIRouter(prefix="/companies", tags=["companies"])

@router.get("", response_model=List[schemas.Company])
async def get_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of all available companies"""
    # Check cache
    cached = cache.get("companies", skip=skip, limit=limit)
    if cached is not None:
        return cached
    
    companies = crud.get_companies(db, skip=skip, limit=limit)
    # Cache for 10 minutes
    cache.set("companies", companies, ttl=600, skip=skip, limit=limit)
    return companies

@router.get("/{symbol}", response_model=schemas.Company)
async def get_company(symbol: str, db: Session = Depends(get_db)):
    """Get a specific company by symbol"""
    # Check cache
    cached = cache.get("company", symbol=symbol)
    if cached is not None:
        return cached
    
    company = crud.get_company(db, symbol=symbol)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Cache for 10 minutes
    cache.set("company", company, ttl=600, symbol=symbol)
    return company

