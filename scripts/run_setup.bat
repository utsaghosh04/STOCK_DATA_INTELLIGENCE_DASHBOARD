@echo off
REM Setup script for Windows

echo Setting up Financial Data Platform...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.9 or higher.
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Initialize database
echo Initializing database...
python scripts\init_db.py

REM Collect initial data
echo Collecting stock market data (this may take a few minutes)...
python scripts\collect_data.py --all

echo Setup complete!
echo.
echo To start the server, run:
echo   venv\Scripts\activate
echo   uvicorn app.main:app --reload
echo.
echo Or use Docker:
echo   docker-compose up

pause

