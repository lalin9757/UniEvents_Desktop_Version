#!/bin/bash
set -e

echo "============================================"
echo " Uni Events Management - Desktop App Setup"
echo "============================================"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python3 not found! Install it first."
    exit 1
fi
echo "[OK] Python3 found: $(python3 --version)"

# Check Node.js
if ! command -v node &>/dev/null; then
    echo "[ERROR] Node.js not found! Install from https://nodejs.org"
    exit 1
fi
echo "[OK] Node.js found: $(node --version)"

echo ""
echo "[1/4] Installing Python dependencies..."
cd django_app
pip3 install -r requirements.txt

echo ""
echo "[2/4] Running Django migrations..."
python3 manage.py migrate

echo ""
echo "[3/4] Collecting static files..."
python3 manage.py collectstatic --noinput
cd ..

echo ""
echo "[4/4] Installing Electron dependencies..."
npm install

echo ""
echo "============================================"
echo " Setup Complete!"
echo "============================================"
echo ""
echo "To run the app:     npm start"
echo "To build for Linux: npm run build:linux"
echo "To build for Mac:   npm run build:mac"
echo ""
