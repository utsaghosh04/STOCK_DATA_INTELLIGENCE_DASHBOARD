"""
Initialize the database with tables and seed companies
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import engine, Base, SessionLocal
from app import models, crud, schemas
from app.services.data_collector import get_all_companies
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Create all tables and seed initial data"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully!")
    
    db = SessionLocal()
    try:
        # Seed companies
        logger.info("Seeding companies...")
        companies = get_all_companies()
        
        for company_data in companies:
            # Check if company already exists
            existing = crud.get_company(db, symbol=company_data["symbol"])
            if not existing:
                company = schemas.CompanyBase(**company_data)
                crud.create_company(db, company)
                logger.info(f"Added company: {company_data['symbol']} - {company_data['name']}")
            else:
                logger.info(f"Company already exists: {company_data['symbol']}")
        
        logger.info("Database initialization complete!")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()

