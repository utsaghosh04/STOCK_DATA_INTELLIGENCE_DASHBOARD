from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Index
from sqlalchemy.sql import func
from app.database import Base

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    sector = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Company(symbol={self.symbol}, name={self.name})>"

class StockData(Base):
    __tablename__ = "stock_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    daily_return = Column(Float, nullable=True)
    moving_avg_7 = Column(Float, nullable=True)
    volatility_score = Column(Float, nullable=True)
    sentiment_index = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_symbol_date', 'symbol', 'date', unique=True),
    )
    
    def __repr__(self):
        return f"<StockData(symbol={self.symbol}, date={self.date}, close={self.close})>"

class StockSummary(Base):
    __tablename__ = "stock_summary"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    week_52_high = Column(Float, nullable=True)
    week_52_low = Column(Float, nullable=True)
    avg_close = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<StockSummary(symbol={self.symbol}, current_price={self.current_price})>"

