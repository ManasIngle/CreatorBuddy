#!/bin/bash

# CreatorIQ Setup Script for Unix/Linux/macOS

set -e

echo "================================================"
echo "  CreatorIQ - AI Creator Growth Intelligence"
echo "================================================"
echo ""

# Check for required tools
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed. Aborting." >&2; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "npm is required but not installed. Aborting." >&2; exit 1; }

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${GREEN}==>${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

# ============================================
# BACKEND SETUP
# ============================================
print_step "Setting up Backend..."

cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_step "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
print_step "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file from .env.example if it doesn't exist
if [ ! -f ".env" ]; then
    print_step "Creating backend .env file..."
    cp .env.example .env
    print_warning "Please edit backend/.env with your actual credentials."
fi

# Run database migrations
print_step "Running database migrations..."
alembic upgrade head

cd ..

# ============================================
# FRONTEND SETUP
# ============================================
print_step "Setting up Frontend..."

cd frontend

# Install dependencies
print_step "Installing Node.js dependencies..."
npm install

# Create .env.local file from .env.example if it doesn't exist
if [ ! -f ".env.local" ]; then
    print_step "Creating frontend .env.local file..."
    cat > .env.local << EOF
# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-here

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
EOF
    print_warning "Please edit frontend/.env.local with your actual credentials."
fi

cd ..

echo ""
echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit the .env files with your credentials:"
echo "   - backend/.env"
echo "   - frontend/.env.local"
echo ""
echo "2. Start PostgreSQL and Redis services"
echo ""
echo "3. Start the Backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload"
echo ""
echo "4. Start the Frontend (separate terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "5. Open http://localhost:3000 in your browser"
echo ""
echo "Alternatively, use Docker:"
echo "   docker-compose up -d"
echo ""
echo "================================================"