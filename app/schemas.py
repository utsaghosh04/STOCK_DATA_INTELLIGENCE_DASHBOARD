from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List

class CompanyBase(BaseModel):
    symbol: str
    name: str
    exchange: str
    sector: Optional[str] = None

class Company(CompanyBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class StockDataBase(BaseModel):
    symbol: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    daily_return: Optional[float] = None
    moving_avg_7: Optional[float] = None
    volatility_score: Optional[float] = None
    sentiment_index: Optional[float] = None

class StockData(StockDataBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class StockSummaryBase(BaseModel):
    symbol: str
    week_52_high: Optional[float] = None
    week_52_low: Optional[float] = None
    avg_close: Optional[float] = None
    current_price: Optional[float] = None

class StockSummary(StockSummaryBase):
    id: int
    last_updated: datetime
    
    class Config:
        from_attributes = True

class ComparisonResponse(BaseModel):
    symbol1: str
    symbol2: str
    correlation: float
    symbol1_data: List[StockData]
    symbol2_data: List[StockData]
    symbol1_summary: StockSummary
    symbol2_summary: StockSummary

class PredictionResponse(BaseModel):
    symbol: str
    current_price: float
    predicted_price: float
    confidence: float
    prediction_date: date

class InsightResponse(BaseModel):
    top_gainers: List[dict]
    top_losers: List[dict]
    most_volatile: List[dict]
    last_updated: datetime

