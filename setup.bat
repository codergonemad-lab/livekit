@echo off

REM LiveKit Video Calling Backend Setup Script for Windows

echo Setting up LiveKit Video Calling Backend...

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create .env file from example
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo Please update the .env file with your actual configuration values.
)

echo Setup complete!
echo.
echo Next steps:
echo 1. Update the .env file with your database and LiveKit configuration
echo 2. Set up your PostgreSQL database
echo 3. Run the server with: python main.py
echo.
echo API Documentation will be available at: http://localhost:8000/docs

pause
