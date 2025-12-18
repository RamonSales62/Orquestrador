@echo off
REM ==================================================
REM EPI ORCHESTRATOR - SETUP SCRIPT (Windows)
REM ==================================================

echo.
echo ================================================
echo   EPI Orchestrator - Setup Script (Windows)
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3 is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/
    exit /b 1
)

echo [OK] Python is installed
python --version

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org/
    exit /b 1
)

echo [OK] Node.js is installed
node --version

echo.
echo ================================================
echo   Setting up Backend...
echo ================================================
echo.

cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [INFO] Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo [OK] Backend dependencies installed

REM Create .env if it doesn't exist
if not exist ".env" (
    copy .env.example .env
    echo [OK] Created backend\.env file
) else (
    echo [INFO] backend\.env already exists
)

cd ..

echo.
echo ================================================
echo   Setting up Frontend...
echo ================================================
echo.

cd frontend

REM Install dependencies
echo Installing Node.js dependencies...
where yarn >nul 2>&1
if errorlevel 1 (
    echo Using npm...
    call npm install
) else (
    echo Using yarn...
    call yarn install
)
echo [OK] Frontend dependencies installed

REM Create .env if it doesn't exist
if not exist ".env" (
    copy .env.example .env
    echo [OK] Created frontend\.env file
) else (
    echo [INFO] frontend\.env already exists
)

cd ..

echo.
echo ================================================
echo   Setup completed successfully!
echo ================================================
echo.
echo Next steps:
echo.
echo 1. Start the Backend:
echo    cd backend
echo    venv\Scripts\activate
echo    uvicorn server:app --reload --host 0.0.0.0 --port 8001
echo.
echo 2. Start the Frontend (in another terminal):
echo    cd frontend
where yarn >nul 2>&1
if errorlevel 1 (
    echo    npm start
) else (
    echo    yarn start
)
echo.
echo 3. Access the application:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8001
echo    API Docs: http://localhost:8001/docs
echo.
echo Tips:
echo    - Edit backend\.env to configure database and CORS
echo    - Edit frontend\.env to configure backend URL
echo    - Check README.md for detailed documentation
echo.
pause
