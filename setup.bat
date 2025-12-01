@echo off
REM EventGraph Setup Script for Windows

echo ======================================
echo EventGraph - Setup Script
echo ======================================
echo.

REM Check Python version
echo Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)
echo Python found

REM Check Docker
echo Checking Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not installed
    echo Please install Docker Desktop from https://www.docker.com/get-started
    exit /b 1
)
echo Docker found

REM Create virtual environment
echo.
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip -q

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt -q
pip install -r requirements-dev.txt -q
echo Dependencies installed

REM Install Playwright browsers
echo Installing Playwright browsers...
playwright install chromium
echo Playwright browsers installed

REM Create .env file
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo .env file created
    echo WARNING: Please edit .env file and add your API keys
) else (
    echo .env file already exists
)

REM Create directories
echo Creating directories...
if not exist "logs" mkdir logs
if not exist "scraped_data" mkdir scraped_data
if not exist "tests\test_data" mkdir tests\test_data
echo Directories created

REM Start Docker services
echo.
echo Starting Docker services...
docker-compose up -d
echo Docker services started

REM Wait for services
echo Waiting for services to start...
timeout /t 5 /nobreak >nul

echo.
echo ======================================
echo Setup Complete!
echo ======================================
echo.
echo Next steps:
echo 1. Edit .env file with your API keys
echo 2. Activate virtual environment: venv\Scripts\activate
echo 3. Run tests: pytest
echo 4. Start application: python src\main.py
echo.
echo Useful commands:
echo - docker-compose logs -f    # View Docker logs
echo - pytest                    # Run tests
echo - python src\main.py        # Start application
echo.
pause
