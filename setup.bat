@echo off
echo ========================================
echo Enterprise Data Pipeline Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

echo [1/6] Creating Python virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
)

echo.
echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo [3/6] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [4/6] Generating sample sales data...
cd src
python generate_data.py
if errorlevel 1 (
    echo ERROR: Failed to generate sample data
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo [5/6] Setting up database (Supabase)...
echo NOTE: Make sure you have updated .env file with your Supabase credentials
echo See SUPABASE_SETUP.md for detailed instructions
echo.
echo Current .env configuration:
type .env
echo.

echo [6/6] Testing Supabase connection...
cd src
python -c "from database import DatabaseManager; db = DatabaseManager(); db.create_database(); db.create_tables(); print('Database setup completed successfully!')"
if errorlevel 1 (
    echo WARNING: Supabase connection failed. Please check your credentials in .env file
    echo See SUPABASE_SETUP.md for setup instructions
    echo You can run this setup again after fixing the configuration
    cd ..
) else (
    echo Supabase connection successful! Database tables created.
    cd ..
)

echo.
echo ========================================
echo Setup completed!
echo ========================================
echo.
echo Next steps:
echo 1. Update .env file with your Supabase credentials (see SUPABASE_SETUP.md)
echo 2. Run: run_pipeline.bat
echo 3. Run: start_dashboard.bat
echo.
echo Files created:
echo - data/raw/sales_data.csv (5,000 sample records with quality issues)
echo - Supabase database tables (if connection successful)
echo - Python virtual environment with all dependencies
echo - SUPABASE_SETUP.md (setup instructions)
echo.
pause