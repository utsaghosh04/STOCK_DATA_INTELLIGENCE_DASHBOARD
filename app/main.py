from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import engine, Base
from app.routers import companies, data, insights
import os

# Create database tables
Base.metadata.create_all(bind=engine)

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
    # Add your GitHub Pages URL here (uncomment and update):
    # "https://yourusername.github.io",
    # Or use regex pattern for all github.io subdomains:
]

# For production, you can set ENVIRONMENT=production and add specific origins
# For now, allowing all origins (update in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production with specific origins
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
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

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

