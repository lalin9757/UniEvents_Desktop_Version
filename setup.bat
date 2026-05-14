@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

echo ============================================
echo  Uni Events Management - Desktop App Setup
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)
echo [OK] Python found

:: Check Node.js
node --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed!
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)
echo [OK] Node.js found

:: Check npm
npm --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] npm is not found!
    pause
    exit /b 1
)
echo [OK] npm found

echo.
echo [1/4] Installing Python dependencies...
cd django_app
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install Python packages!
    pause
    exit /b 1
)

echo.
echo [2/4] Running Django migrations...
python manage.py migrate
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Migration failed!
    pause
    exit /b 1
)

echo.
echo [3/4] Collecting static files...
python manage.py collectstatic --noinput
cd ..

echo.
echo [4/4] Installing Electron dependencies...
npm install
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] npm install failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Setup Complete!
echo ============================================
echo.
echo To run the app:   npm start
echo To build .exe:    npm run build:win
echo.
pause
