# Stock Data Intelligence Dashboard

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
- **Visualization**: Chart.js
- **ML**: scikit-learn
- **Caching**: In-memory cache with TTL

## Local Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 12+ (optional - SQLite works by default)

### Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python scripts/init_db.py
```

4. Collect initial data:
```bash
python scripts/collect_data.py --all
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

6. Access the application:
- Dashboard: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Deployment Guide

This guide will walk you through deploying the frontend to GitHub Pages and the backend to Render.

---

## Part 1: Deploy Backend to Render

### Step 1: Create Render Account

1. Go to [render.com](https://render.com)
2. Click **"Get Started for Free"** or **"Sign Up"**
3. Sign up with GitHub (recommended) or email
4. Verify your email if required

### Step 2: Create Web Service

1. **Go to Render Dashboard**: [dashboard.render.com](https://dashboard.render.com)
2. **Click "New +"** → **"Web Service"**
3. **Connect Repository**:
   - If not connected, click **"Connect GitHub"**
   - Authorize Render to access your repositories
   - Select your repository: `STOCK_DATA_INTELLIGENCE_DASHBOARD`
   - Click **"Connect"**

4. **Configure Service**:
   - **Name**: `stock-data-backend` (or your preferred name)
   - **Region**: Choose closest to you (e.g., `Oregon (US West)`)
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: Select **Free**

5. **Environment Variables** (Optional):
   - Click **"Advanced"** → **"Add Environment Variable"**
   - `DATABASE_URL`: `sqlite:///./financial_data.db` (for SQLite)
   - `ENVIRONMENT`: `production`
   - `LOG_LEVEL`: `INFO`

6. **Click "Create Web Service"**

### Step 3: Wait for Deployment

1. Render will start building your service
2. Watch the build logs in real-time
3. First deployment takes 5-10 minutes
4. Wait for "Your service is live" message

### Step 4: Get Your Backend URL

Once deployed, Render will provide a URL like:
```
https://stock-data-backend.onrender.com
```

**⚠️ IMPORTANT**: Save this URL - you'll need it for the frontend!

### Step 5: Initialize Database

After first deployment:

1. In Render dashboard, go to your service
2. Click **"Shell"** tab
3. Run these commands:
   ```bash
   python scripts/init_db.py
   python scripts/collect_data.py --all
   ```
4. Wait for data collection to complete

### Step 6: Test Your Backend

Test these URLs:
- Health: `https://your-backend-url.onrender.com/health`
- API Docs: `https://your-backend-url.onrender.com/docs`
- Companies: `https://your-backend-url.onrender.com/companies`

---

## Part 2: Deploy Frontend to GitHub Pages

### Step 1: Update Frontend Configuration

1. **Edit `static/js/config.js`**:
   ```javascript
   const API_BASE_PRODUCTION = 'https://your-backend-url.onrender.com';
   ```
   Replace `your-backend-url.onrender.com` with your actual Render URL from Part 1, Step 4.

2. **Commit the change**:
   ```bash
   git add static/js/config.js
   git commit -m "Update backend URL for production"
   git push
   ```

### Step 2: Enable GitHub Pages

1. **Go to your repository** on GitHub:
   ```
   https://github.com/YOUR_USERNAME/STOCK_DATA_INTELLIGENCE_DASHBOARD
   ```

2. **Click "Settings"** (top menu bar)

3. **Click "Pages"** (left sidebar, under "Code and automation")

4. **Under "Source"**, select:
   - **Source**: `Deploy from a branch`
   - **Branch**: `main`
   - **Folder**: `/ (root)`

5. **Click "Save"**

6. **Wait a few seconds** - you should see:
   - ✅ Green checkmark
   - ✅ Message: "Your site is live at https://yourusername.github.io/STOCK_DATA_INTELLIGENCE_DASHBOARD"

### Step 3: Configure CORS in Backend

1. **Edit `app/main.py`**:
   Find the CORS configuration and update it:
   ```python
   cors_origins = [
       "http://localhost:8000",
       "http://127.0.0.1:8000",
       "https://yourusername.github.io",  # Add your GitHub Pages URL
   ]
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=cors_origins + ["*"],  # Allow all for now
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```
   Replace `yourusername` with your GitHub username.

2. **Commit and push**:
   ```bash
   git add app/main.py
   git commit -m "Update CORS for GitHub Pages"
   git push
   ```

3. **Render will automatically redeploy** (takes 2-3 minutes)

### Step 4: Verify GitHub Pages Deployment

1. **Go to "Actions" tab** in your repository
2. **Check the workflow** - it should run automatically after you enabled Pages
3. **If workflow fails**, click on it and check the logs
4. **If workflow succeeds**, your site is deployed!

### Step 5: Access Your Live Site

Your frontend will be available at:
```
https://yourusername.github.io/STOCK_DATA_INTELLIGENCE_DASHBOARD
```

---

## Part 3: Final Configuration

### Update CORS (Important!)

After deploying frontend, make sure your backend allows requests from GitHub Pages:

1. **Go to Render dashboard** → Your service → **Environment**
2. **Add environment variable**:
   - Key: `CORS_ORIGINS`
   - Value: `https://yourusername.github.io`
3. **Or update `app/main.py`** directly (as shown in Part 2, Step 3)

### Test Everything

1. **Frontend**: Visit `https://yourusername.github.io/STOCK_DATA_INTELLIGENCE_DASHBOARD`
2. **Check browser console** (F12) for any errors
3. **Test features**:
   - Load companies list
   - View stock data
   - Check charts
   - Test comparison feature

---

## Troubleshooting

### Backend Issues

**Problem**: Build fails on Render
- **Solution**: 
  - Check build logs in Render dashboard for specific error
  - Ensure all dependencies are in `requirements.txt`
  - Verify Python version (add `runtime.txt` with `python-3.11.0` if needed)
  - Check that build command is: `pip install -r requirements.txt`

**Problem**: "No module named 'app'" error
- **Solution**: Verify start command is: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Problem**: "Port already in use" error
- **Solution**: Make sure start command uses `$PORT` environment variable (not hardcoded port)

**Problem**: Service crashes on startup
- **Solution**: 
  - Check runtime logs in Render dashboard
  - Verify start command uses `$PORT`
  - Check for import errors in logs
  - Ensure database path is relative (for SQLite): `sqlite:///./financial_data.db`

**Problem**: Database not initialized
- **Solution**: Use Render Shell to run `python scripts/init_db.py`

**Problem**: Slow first request
- **Solution**: Normal on free tier - service spins down after 15 min inactivity. First request takes 30-60 seconds.

**Problem**: Dependencies installation fails
- **Solution**: 
  - Check `requirements.txt` for version conflicts
  - Some packages may need specific versions
  - Try removing version pins and let pip resolve

### Frontend Issues

**Problem**: API calls fail with CORS error
- **Solution**: Update CORS in `app/main.py` with your GitHub Pages URL

**Problem**: API calls fail (404 or connection error)
- **Solution**: Check `static/js/config.js` has correct backend URL

**Problem**: GitHub Pages workflow fails
- **Solution**: Make sure Pages is enabled in Settings → Pages first

**Problem**: Files not loading
- **Solution**: Check file paths are relative (not starting with `/`)

---

## Quick Reference

### Backend URLs
- **Render Service**: `https://your-backend-name.onrender.com`
- **Health Check**: `https://your-backend-name.onrender.com/health`
- **API Docs**: `https://your-backend-name.onrender.com/docs`

### Frontend URLs
- **GitHub Pages**: `https://yourusername.github.io/STOCK_DATA_INTELLIGENCE_DASHBOARD`

### Important Files
- **Backend Config**: `app/main.py` (CORS settings)
- **Frontend Config**: `static/js/config.js` (API URL)
- **Workflow**: `.github/workflows/deploy-pages.yml` (auto-deployment)

---

## Deployment Checklist

### Backend (Render)
- [ ] Render account created
- [ ] Web service created and connected to GitHub
- [ ] Service deployed successfully
- [ ] Backend URL saved
- [ ] Database initialized via Shell
- [ ] Data collected via Shell
- [ ] Health endpoint works
- [ ] API docs accessible

### Frontend (GitHub Pages)
- [ ] `static/js/config.js` updated with backend URL
- [ ] Changes committed and pushed
- [ ] GitHub Pages enabled in Settings
- [ ] Workflow runs successfully
- [ ] Frontend accessible at GitHub Pages URL
- [ ] CORS updated in backend
- [ ] Backend redeployed with CORS changes

### Testing
- [ ] Frontend loads correctly
- [ ] API calls work from frontend
- [ ] Companies list loads
- [ ] Stock data displays
- [ ] Charts render correctly
- [ ] All features work

---

## API Endpoints

- `GET /companies` - List all available companies
- `GET /data/{symbol}` - Get last 30 days of stock data
- `GET /data/summary/{symbol}` - Get 52-week high, low, and average
- `GET /data/compare?symbol1=X&symbol2=Y` - Compare two stocks
- `GET /insights` - Get top gainers/losers and insights
- `GET /insights/predict/{symbol}` - Get price prediction for a stock

API documentation available at: `https://your-backend-url.onrender.com/docs`

## Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database operations
│   ├── cache.py             # Caching layer
│   ├── services/            # Business logic
│   │   ├── data_collector.py
│   │   ├── data_processor.py
│   │   └── ml_predictor.py
│   └── routers/             # API routes
│       ├── companies.py
│       ├── data.py
│       └── insights.py
├── scripts/
│   ├── init_db.py          # Database initialization
│   └── collect_data.py     # Data collection
├── static/                  # Frontend files
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── app.js
│       └── config.js       # API configuration
├── .github/workflows/
│   └── deploy-pages.yml    # GitHub Pages deployment
├── render.yaml             # Render deployment config
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Notes

- **Free Tier Limitations**: Render free tier services spin down after 15 minutes of inactivity. First request after spin-down takes 30-60 seconds.
- **Auto-Deployment**: Both GitHub Pages and Render automatically deploy when you push to the main branch.
- **Database**: Uses SQLite by default. For production, consider PostgreSQL (available on Render).

## Support

For issues or questions:
- **Render Docs**: https://render.com/docs
- **GitHub Pages Docs**: https://docs.github.com/en/pages
- **API Documentation**: Available at `/docs` endpoint

---

**Your application is now live! 🚀**
