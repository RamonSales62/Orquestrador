#!/usr/bin/env bash

# ==================================================
# EPI ORCHESTRATOR - SETUP SCRIPT (Linux/macOS)
# ==================================================

set -e

echo "🛡️  EPI Orchestrator - Setup Script"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.11+ first.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d " " -f 2 | cut -d "." -f 1,2)
echo -e "${GREEN}✓${NC} Python version: $PYTHON_VERSION"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 16+ first.${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✓${NC} Node.js version: $NODE_VERSION"

echo ""
echo "📦 Setting up Backend..."
echo "------------------------"

# Setup Backend
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${YELLOW}ℹ${NC} Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓${NC} Backend dependencies installed"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓${NC} Created backend/.env file"
else
    echo -e "${YELLOW}ℹ${NC} backend/.env already exists"
fi

cd ..

echo ""
echo "📦 Setting up Frontend..."
echo "-------------------------"

# Setup Frontend
cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
if command -v yarn &> /dev/null; then
    echo "Using yarn..."
    yarn install
else
    echo "Using npm..."
    npm install
fi
echo -e "${GREEN}✓${NC} Frontend dependencies installed"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓${NC} Created frontend/.env file"
else
    echo -e "${YELLOW}ℹ${NC} frontend/.env already exists"
fi

cd ..

echo ""
echo "======================================"
echo -e "${GREEN}✅ Setup completed successfully!${NC}"
echo "======================================"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Start the Backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn server:app --reload --host 0.0.0.0 --port 8001"
echo ""
echo "2. Start the Frontend (in another terminal):"
echo "   cd frontend"
if command -v yarn &> /dev/null; then
    echo "   yarn start"
else
    echo "   npm start"
fi
echo ""
echo "3. Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8001"
echo "   API Docs: http://localhost:8001/docs"
echo ""
echo "💡 Tips:"
echo "   - Edit backend/.env to configure database and CORS"
echo "   - Edit frontend/.env to configure backend URL"
echo "   - Check README.md for detailed documentation"
echo ""
