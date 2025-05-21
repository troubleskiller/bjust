@echo off
echo Initializing Flask Environment

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

echo Creating virtual environment...
python -m venv venv
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to create virtual environment
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to install dependencies
    exit /b 1
)

echo Initializing database migrations...
flask db init
if %ERRORLEVEL% neq 0 (
    echo Warning: Migration initialization failed. It might already exist.
)

echo Setup completed successfully!
echo.

REM Return success
exit /b 0 