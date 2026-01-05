# Git Setup and Push Guide

## Push Code to STOCK_DATA_INTELLIGENCE_DASHBOARD Repository

### Step 1: Initialize Git (if not already done)

```bash
# Check if git is initialized
git status

# If not initialized, run:
git init
```

### Step 2: Create .gitignore (if not exists)

Make sure `.gitignore` includes:
- `__pycache__/`
- `*.pyc`
- `venv/`
- `.env`
- `*.db`
- `*.sqlite`

### Step 3: Add All Files

```bash
git add .
```

### Step 4: Create Initial Commit

```bash
git commit -m "Initial commit: Financial Data Platform with full features"
```

### Step 5: Add Remote Repository

```bash
# If repository doesn't exist on GitHub, create it first at github.com
# Then add remote:

git remote add origin https://github.com/YOUR_USERNAME/STOCK_DATA_INTELLIGENCE_DASHBOARD.git

# Or if using SSH:
git remote add origin git@github.com:YOUR_USERNAME/STOCK_DATA_INTELLIGENCE_DASHBOARD.git
```

### Step 6: Push to GitHub

```bash
# Push to main branch
git branch -M main
git push -u origin main
```

---

## If Repository Already Exists

If the repository already exists and has content:

```bash
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/STOCK_DATA_INTELLIGENCE_DASHBOARD.git

# Pull existing content (if any)
git pull origin main --allow-unrelated-histories

# Resolve any conflicts, then:
git add .
git commit -m "Merge with existing repository"

# Push
git push -u origin main
```

---

## Quick Commands Summary

```bash
# Initialize and setup
git init
git add .
git commit -m "Initial commit: Financial Data Platform"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/STOCK_DATA_INTELLIGENCE_DASHBOARD.git

# Push
git branch -M main
git push -u origin main
```

---

## After Pushing

1. **Verify on GitHub**: Check your repository at `https://github.com/YOUR_USERNAME/STOCK_DATA_INTELLIGENCE_DASHBOARD`

2. **Enable GitHub Pages**: 
   - Go to Settings → Pages
   - Source: Deploy from branch
   - Branch: main
   - Folder: / (root)

3. **Deploy Backend to Render**:
   - Follow `RENDER_DEPLOYMENT.md`
   - Use repository: `STOCK_DATA_INTELLIGENCE_DASHBOARD`

4. **Update Config**:
   - Update `static/js/config.js` with Render backend URL
   - Commit and push again

---

## Troubleshooting

**Error: remote origin already exists**
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/STOCK_DATA_INTELLIGENCE_DASHBOARD.git
```

**Error: failed to push**
```bash
# Make sure you're authenticated
# Or use SSH instead of HTTPS
```

**Error: branch main already exists**
```bash
git branch -M main
git push -u origin main --force  # Use with caution
```

