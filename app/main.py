from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import engine, Base, SessionLocal
from app.routers import companies, data, insights
from app import crud, schemas
from app.services.data_collector import get_all_companies
import os
import logging

logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Auto-initialize companies on startup (if not already initialized)
def init_companies_on_startup():
    """Initialize companies table if empty"""
    try:
        db = SessionLocal()
        try:
            # Check if companies exist
            existing_companies = crud.get_companies(db, limit=1)
            if not existing_companies:
                logger.info("No companies found. Initializing companies...")
                companies = get_all_companies()
                for company_data in companies:
                    existing = crud.get_company(db, symbol=company_data["symbol"])
                    if not existing:
                        company = schemas.CompanyBase(**company_data)
                        crud.create_company(db, company)
                logger.info(f"Initialized {len(companies)} companies")
            else:
                logger.info("Companies already initialized")
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Could not auto-initialize companies: {str(e)}")
        # Don't fail startup if initialization fails

# Run initialization
init_companies_on_startup()

# Initialize FastAPI app
app = FastAPI(
    title="Financial Data Platform API",
    description="A comprehensive API for stock market data, analysis, and predictions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
# Update allow_origins with your GitHub Pages URL in production
import os
cors_origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://utsaghosh04.github.io",
    "https://utsaghosh04.github.io/STOCK_DATA_INTELLIGENCE_DASHBOARD",
]

# Allow all origins for now (update in production with specific origins)
# In production, you can restrict to: allow_origins=cors_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins - update to cors_origins for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(companies.router)
app.include_router(data.router)
app.include_router(insights.router)

# Serve static files (frontend)
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    # Mount static files directory
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # Also serve individual static file types
    app.mount("/css", StaticFiles(directory=os.path.join(static_dir, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(static_dir, "js")), name="js")

@app.get("/")
async def root():
    """Root endpoint - serve the dashboard"""
    static_file = os.path.join(static_dir, "index.html")
    if os.path.exists(static_file):
        return FileResponse(static_file)
    return {
        "message": "Financial Data Platform API",
        "docs": "/docs",
        "endpoints": {
            "companies": "/companies",
            "stock_data": "/data/{symbol}",
            "summary": "/data/summary/{symbol}",
            "compare": "/data/compare?symbol1=X&symbol2=Y",
            "insights": "/insights",
            "predict": "/insights/predict/{symbol}"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "financial-data-platform"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

