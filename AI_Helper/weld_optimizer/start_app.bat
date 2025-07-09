@echo off
echo ========================================
echo    Weld Parameter Optimizer Launcher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

REM Change to the script directory
cd /d "%~dp0"

REM Check if setup has been run
if not exist "database\weld_parameters.db" (
    echo Database not found. Running initial setup...
    python setup.py
    if errorlevel 1 (
        echo Setup failed. Please check the error messages above.
        pause
        exit /b 1
    )
    echo.
)

echo Starting Weld Parameter Optimizer...
echo.
echo The web application will be available at:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

cd web_app
python app.py

pause
