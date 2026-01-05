# GitHub Pages Deployment - Quick Guide

## Quick Steps

### 1. Update Backend URL

Edit `static/js/config.js` and set your deployed backend URL:

```javascript
const API_BASE_PRODUCTION = 'https://your-backend.onrender.com';
```

### 2. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under **Source**, select:
   - **Branch**: `main` (or `gh-pages`)
   - **Folder**: `/ (root)` or `/docs`
4. Click **Save**

### 3. Deploy

**Option A: Automatic (GitHub Actions)**
- Just push to `main` branch
- GitHub Actions will automatically deploy
- Check Actions tab for status

**Option B: Manual**
```bash
# The static files are already in the static/ folder
# GitHub Pages will serve them automatically
git add .
git commit -m "Deploy to GitHub Pages"
git push origin main
```

### 4. Access Your Site

Your site will be available at:
```
https://yourusername.github.io/repository-name
```

---

## Important Notes

### Backend Deployment Required

GitHub Pages only serves static files. You **must** deploy the backend separately:

- **Render** (Recommended - Free): https://render.com
- **Railway**: https://railway.app
- **Fly.io**: https://fly.io
- **Heroku**: https://heroku.com

See `DEPLOYMENT.md` for detailed backend deployment instructions.

### Update CORS

After deploying backend, update `app/main.py` to allow your GitHub Pages domain:

```python
cors_origins = [
    "https://yourusername.github.io",
    # ... other origins
]
```

### File Paths

The frontend uses relative paths (e.g., `css/style.css` instead of `/static/css/style.css`) so it works on GitHub Pages.

---

## Testing Locally

Before deploying, test that the frontend works:

```bash
# Serve static files locally
cd static
python -m http.server 8080

# Or use any static file server
# Then visit http://localhost:8080
```

---

## Troubleshooting

**Problem**: API calls fail
- **Solution**: Check `config.js` has correct backend URL

**Problem**: Files not loading
- **Solution**: Ensure paths are relative (not starting with `/`)

**Problem**: CORS errors
- **Solution**: Update CORS settings in backend `app/main.py`

---

## Next Steps

1. ✅ Deploy backend (see `DEPLOYMENT.md`)
2. ✅ Update `static/js/config.js` with backend URL
3. ✅ Enable GitHub Pages
4. ✅ Push to main branch
5. ✅ Test your deployed site!

