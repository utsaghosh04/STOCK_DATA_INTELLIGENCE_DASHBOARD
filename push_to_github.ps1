# PowerShell script to push code to GitHub repository
# STOCK_DATA_INTELLIGENCE_DASHBOARD

Write-Host "Setting up Git repository..." -ForegroundColor Green

# Initialize git if not already done
if (-not (Test-Path .git)) {
    Write-Host "Initializing git repository..." -ForegroundColor Yellow
    git init
}

# Check if remote already exists
$remoteExists = git remote -v | Select-String "STOCK_DATA_INTELLIGENCE_DASHBOARD"

if (-not $remoteExists) {
    Write-Host "`nPlease enter your GitHub username:" -ForegroundColor Cyan
    $username = Read-Host
    
    Write-Host "`nAdding remote repository..." -ForegroundColor Yellow
    git remote add origin "https://github.com/$username/STOCK_DATA_INTELLIGENCE_DASHBOARD.git"
    Write-Host "Remote added: https://github.com/$username/STOCK_DATA_INTELLIGENCE_DASHBOARD.git" -ForegroundColor Green
} else {
    Write-Host "Remote already exists" -ForegroundColor Yellow
    git remote -v
}

# Add all files
Write-Host "`nAdding all files..." -ForegroundColor Yellow
git add .

# Check if there are changes to commit
$status = git status --porcelain
if ($status) {
    Write-Host "`nCreating commit..." -ForegroundColor Yellow
    git commit -m "Initial commit: Financial Data Platform - Stock Data Intelligence Dashboard"
    Write-Host "Commit created successfully!" -ForegroundColor Green
} else {
    Write-Host "`nNo changes to commit" -ForegroundColor Yellow
}

# Set branch to main
Write-Host "`nSetting branch to main..." -ForegroundColor Yellow
git branch -M main

# Push to GitHub
Write-Host "`nPushing to GitHub..." -ForegroundColor Yellow
Write-Host "You may be prompted for GitHub credentials" -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "Repository: https://github.com/$username/STOCK_DATA_INTELLIGENCE_DASHBOARD" -ForegroundColor Cyan
} else {
    Write-Host "`n❌ Push failed. Please check:" -ForegroundColor Red
    Write-Host "1. Repository exists on GitHub" -ForegroundColor Yellow
    Write-Host "2. You have push permissions" -ForegroundColor Yellow
    Write-Host "3. GitHub credentials are correct" -ForegroundColor Yellow
}

