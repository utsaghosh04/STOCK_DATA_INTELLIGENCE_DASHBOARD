# Mini Financial Data Platform

A comprehensive financial data platform that collects, processes, and visualizes stock market data with REST APIs and an interactive dashboard.

## ✅ Assignment Requirements - All Completed

### Part 1: Data Collection & Preparation ✅
- ✅ Stock market data collection using yfinance API
- ✅ Data cleaning with Pandas (missing values, date conversion)
- ✅ Daily Return calculation: `(CLOSE - OPEN) / OPEN`
- ✅ 7-day Moving Average
- ✅ 52-week High/Low calculation
- ✅ **Custom Metrics**: Volatility Score, Sentiment Index, Correlation Analysis

### Part 2: Backend API Development ✅
- ✅ `GET /companies` - List all companies
- ✅ `GET /data/{symbol}` - Last 30 days of stock data
- ✅ `GET /data/summary/{symbol}` - 52-week high, low, average
- ✅ `GET /data/compare?symbol1=X&symbol2=Y` - Compare stocks
- ✅ Swagger documentation at `/docs`

### Part 3: Visualization Dashboard ✅
- ✅ Company list with interactive selection
- ✅ Closing price charts (Chart.js)
- ✅ Time filters (30/90/180/365 days)
- ✅ Stock comparison feature
- ✅ Top Gainers/Losers insights
- ✅ ML price prediction

### Part 4: Optional Add-ons ✅
- ✅ Docker & Docker Compose
- ✅ ML price prediction (Linear Regression)
- ✅ Caching layer (in-memory with TTL)
- ✅ Async API endpoints

## Features

- **Data Collection**: Automated collection of stock market data using yfinance with mock data fallback
- **Data Processing**: Cleaning, transformation, and calculation of financial metrics
- **REST APIs**: FastAPI-based endpoints for accessing stock data
- **Visualization Dashboard**: Interactive charts and insights
- **ML Predictions**: Simple price prediction using machine learning
- **Docker Support**: Containerized deployment

## Tech Stack

- **Backend**: FastAPI, PostgreSQL, SQLAlchemy
- **Data Processing**: Pandas, NumPy
- **Data Source**: yfinance
- **Visualization**: Chart.js, Plotly
- **ML**: scikit-learn
- **Caching**: Redis
- **Deployment**: Docker, Docker Compose

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Docker (optional)

### Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. Initialize the database:
```bash
python scripts/init_db.py
```

5. Collect initial data:
```bash
python scripts/collect_data.py
```

6. Run the application:
```bash
uvicorn app.main:app --reload
```

### Docker Setup

```bash
docker-compose up -d
```

### Deployment

- **Frontend**: Deploy to GitHub Pages (see `GITHUB_PAGES_SETUP.md`)
- **Backend**: Deploy to Render (see `RENDER_DEPLOYMENT.md` or `RENDER_QUICK_START.md`)
- **Full Guide**: See `DEPLOYMENT.md` for complete deployment instructions

## API Endpoints

- `GET /companies` - List all available companies
- `GET /data/{symbol}` - Get last 30 days of stock data
- `GET /summary/{symbol}` - Get 52-week high, low, and average
- `GET /compare?symbol1=X&symbol2=Y` - Compare two stocks
- `GET /predict/{symbol}` - Get price prediction for a stock
- `GET /insights` - Get top gainers/losers and insights

API documentation available at: `http://localhost:8000/docs`

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database operations
│   ├── services/            # Business logic
│   │   ├── data_collector.py
│   │   ├── data_processor.py
│   │   └── ml_predictor.py
│   └── routers/             # API routes
│       ├── companies.py
│       ├── data.py
│       └── insights.py
├── scripts/
│   ├── init_db.py
│   └── collect_data.py
├── static/                  # Frontend files
│   ├── index.html
│   ├── css/
│   └── js/
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

