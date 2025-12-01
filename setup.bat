@echo off
REM CreatorIQ Setup Script for Windows

echo ================================================
echo   CreatorIQ - AI Creator Growth Intelligence
echo ================================================
echo.

REM Check for required tools
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is required but not installed. Aborting.
    exit /b 1
)

where npm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo npm is required but not installed. Aborting.
    exit /b 1
)

REM ============================================
REM BACKEND SETUP
REM ============================================
echo ==^> Setting up Backend...

cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo ==^> Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment and install dependencies
echo ==^> Installing Python dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

REM Create .env file from .env.example if it doesn't exist
if not exist ".env" (
    echo ==^> Creating backend .env file...
    copy .env.example .env
    echo WARNING: Please edit backend/.env with your actual credentials.
)

REM Run database migrations
echo ==^> Running database migrations...
alembic upgrade head

cd ..

REM ============================================
REM FRONTEND SETUP
REM ============================================
echo ==^> Setting up Frontend...

cd frontend

REM Install dependencies
echo ==^> Installing Node.js dependencies...
call npm install

REM Create .env.local file if it doesn't exist
if not exist ".env.local" (
    echo ==^> Creating frontend .env.local file...
    (
        echo # NextAuth Configuration
        echo NEXTAUTH_URL=http://localhost:3000
        echo NEXTAUTH_SECRET=your-secret-here
        echo.
        echo # Backend API URL
        echo NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
        echo.
        echo # Google OAuth
        echo GOOGLE_CLIENT_ID=your-google-client-id
        echo GOOGLE_CLIENT_SECRET=your-google-client-secret
    ) > .env.local
    echo WARNING: Please edit frontend/.env.local with your actual credentials.
)

cd ..

echo.
echo ================================================
echo   Setup Complete!
echo ================================================
echo.
echo Next steps:
echo.
echo 1. Edit the .env files with your credentials:
echo    - backend/.env
echo    - frontend/.env.local
echo.
echo 2. Start PostgreSQL and Redis services
echo.
echo 3. Start the Backend:
echo    cd backend
echo    venv\Scripts\activate.bat
echo    uvicorn app.main:app --reload
echo.
echo 4. Start the Frontend (separate command prompt):
echo    cd frontend
echo    npm run dev
echo.
echo 5. Open http://localhost:3000 in your browser
echo.
echo Alternatively, use Docker:
echo    docker-compose up -d
echo.
echo ================================================

pause