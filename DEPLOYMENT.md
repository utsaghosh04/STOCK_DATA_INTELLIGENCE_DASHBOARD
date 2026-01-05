# Deployment Guide

This guide explains how to deploy the Financial Data Platform to production.

## Architecture

The application consists of two parts:
1. **Frontend** (Static files) - Deploy to GitHub Pages
2. **Backend** (FastAPI) - Deploy to a cloud service (Render, Railway, Fly.io, etc.)

---

## Part 1: Deploy Frontend to GitHub Pages

### Step 1: Prepare Repository

1. **Enable GitHub Pages**:
   - Go to your repository on GitHub
   - Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main` (or `gh-pages`)
   - Folder: `/ (root)` or `/docs`

2. **Update API Configuration**:
   - Edit `static/js/config.js`
   - Set `API_BASE_PRODUCTION` to your deployed backend URL
   - Example: `const API_BASE_PRODUCTION = 'https://financial-api.onrender.com';`

### Step 2: Deploy Using GitHub Actions (Recommended)

The repository includes a GitHub Actions workflow (`.github/workflows/deploy-pages.yml`) that automatically deploys the frontend when you push to main.

1. **Commit and push**:
   ```bash
   git add .
   git commit -m "Setup GitHub Pages deployment"
   git push origin main
   ```

2. **Check deployment**:
   - Go to Actions tab in GitHub
   - Wait for the workflow to complete
   - Your site will be available at: `https://yourusername.github.io/repository-name`

### Step 3: Manual Deployment (Alternative)

If you prefer manual deployment:

1. **Build static files**:
   ```bash
   # Copy static files to docs folder (GitHub Pages can serve from /docs)
   mkdir -p docs
   cp -r static/* docs/
   ```

2. **Update paths in docs/index.html**:
   - Change `/static/` paths to relative paths
   - Or use the root deployment method

3. **Commit and push**:
   ```bash
   git add docs/
   git commit -m "Deploy frontend to GitHub Pages"
   git push origin main
   ```

---

## Part 2: Deploy Backend to Cloud Service

### Option A: Render (Recommended - Free Tier Available)

1. **Create Account**: Sign up at [render.com](https://render.com)

2. **Create New Web Service**:
   - Connect your GitHub repository
   - Select the repository
   - Configure:
     - **Name**: financial-data-platform
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - **Environment Variables**:
       ```
       DATABASE_URL=sqlite:///./financial_data.db
       PORT=8000
       ```

3. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment
   - Your API will be at: `https://your-app.onrender.com`

4. **Update Frontend Config**:
   - Update `static/js/config.js` with your Render URL
   - Redeploy frontend

### Option B: Railway

1. **Create Account**: Sign up at [railway.app](https://railway.app)

2. **New Project**:
   - Click "New Project"
   - Deploy from GitHub repo
   - Select your repository

3. **Configure**:
   - Railway auto-detects Python
   - Add environment variables if needed
   - Deploy

4. **Get URL**: Your API will be at `https://your-app.railway.app`

### Option C: Fly.io

1. **Install Fly CLI**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**:
   ```bash
   fly auth login
   ```

3. **Create App**:
   ```bash
   fly launch
   ```

4. **Deploy**:
   ```bash
   fly deploy
   ```

### Option D: Heroku

1. **Install Heroku CLI**

2. **Login**:
   ```bash
   heroku login
   ```

3. **Create App**:
   ```bash
   heroku create your-app-name
   ```

4. **Add Buildpack**:
   ```bash
   heroku buildpacks:set heroku/python
   ```

5. **Deploy**:
   ```bash
   git push heroku main
   ```

---

## Part 3: Database Setup

### For Production (PostgreSQL)

1. **Add PostgreSQL** (Render/Railway):
   - Add PostgreSQL service
   - Get connection string
   - Set as `DATABASE_URL` environment variable

2. **Initialize Database**:
   ```bash
   # SSH into your deployment or use one-off command
   python scripts/init_db.py
   python scripts/collect_data.py --all
   ```

### For Simple Deployment (SQLite)

- SQLite works out of the box
- Data persists in the container/filesystem
- Not recommended for production with multiple instances

---

## Part 4: Environment Variables

Set these in your backend deployment:

```bash
DATABASE_URL=postgresql://user:pass@host:port/dbname  # For PostgreSQL
# OR
DATABASE_URL=sqlite:///./financial_data.db  # For SQLite

REDIS_URL=redis://host:port  # Optional, for caching
LOG_LEVEL=INFO
```

---

## Part 5: CORS Configuration

Update `app/main.py` to allow your GitHub Pages domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourusername.github.io",
        "http://localhost:8000",  # For local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Complete Deployment Checklist

### Frontend (GitHub Pages)
- [ ] Repository is public (or GitHub Pro for private)
- [ ] GitHub Pages is enabled
- [ ] `static/js/config.js` has correct backend URL
- [ ] GitHub Actions workflow is set up
- [ ] Frontend is accessible at GitHub Pages URL

### Backend (Cloud Service)
- [ ] Backend is deployed and accessible
- [ ] Environment variables are set
- [ ] Database is initialized
- [ ] Data collection script has run
- [ ] CORS is configured for frontend domain
- [ ] Health check endpoint works: `/health`

### Testing
- [ ] Frontend loads correctly
- [ ] API calls work from frontend
- [ ] Companies list loads
- [ ] Stock data displays
- [ ] Charts render correctly
- [ ] All endpoints work

---

## Troubleshooting

### Frontend Issues

**Problem**: API calls fail with CORS error
- **Solution**: Update CORS settings in `app/main.py` to include your GitHub Pages domain

**Problem**: Static files not loading
- **Solution**: Check file paths are relative (not `/static/` but `css/style.css`)

**Problem**: API_BASE not set
- **Solution**: Ensure `config.js` is loaded before `app.js` in `index.html`

### Backend Issues

**Problem**: Database connection fails
- **Solution**: Check `DATABASE_URL` environment variable

**Problem**: No data available
- **Solution**: Run `python scripts/init_db.py` and `python scripts/collect_data.py --all`

**Problem**: Port binding error
- **Solution**: Use `$PORT` environment variable or `0.0.0.0` as host

---

## Example URLs

After deployment:
- **Frontend**: `https://yourusername.github.io/financial-data-platform`
- **Backend API**: `https://financial-api.onrender.com`
- **API Docs**: `https://financial-api.onrender.com/docs`

---

## Continuous Deployment

Both GitHub Pages and cloud services support automatic deployment:
- **GitHub Pages**: Deploys on push to main branch
- **Render/Railway**: Deploys on push to main branch (if connected)

Just push your code and both will update automatically!

---

## Cost Estimate

- **GitHub Pages**: Free (for public repos)
- **Render**: Free tier available (with limitations)
- **Railway**: Free tier available (with $5 credit)
- **Fly.io**: Free tier available
- **Heroku**: No free tier (paid plans)

**Recommended**: Render or Railway for backend (free tiers available)

