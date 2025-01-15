@echo off
echo Starting Movement Labs AI Assistant installation...

REM Check Python version
python --version > tmp.txt 2>&1
set /p python_version=<tmp.txt
del tmp.txt

echo Current Python version: %python_version%
echo Required: Python 3.10 or higher

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo Creating necessary directories...
mkdir data\vector_db 2>nul
mkdir data\docs 2>nul

REM Copy environment file if it doesn't exist
if not exist .env (
    echo Creating .env file from example...
    copy .env.example .env
    echo Created .env file. Please edit it with your credentials.
)

echo.
echo Installation complete!
echo.
echo Next steps:
echo 1. Edit the .env file with your credentials
echo 2. Run the bot in test mode: set TEST_MODE=true ^& python src/main.py
echo 3. Once tested, run in production: python src/main.py
echo.
pause 