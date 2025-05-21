@echo off
echo Flask Application Manager

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Running initialization...
    call init.bat
    if %ERRORLEVEL% neq 0 (
        echo Error: Initialization failed
        exit /b 1
    )
) else (
    REM If venv exists, check if requirements are installed
    echo Checking environment...
    call venv\Scripts\activate.bat
    
    REM Quick check if key packages are installed
    pip show flask >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo Some dependencies are missing. Installing requirements...
        pip install -r requirements.txt
        if %ERRORLEVEL% neq 0 (
            echo Error: Failed to install dependencies
            exit /b 1
        )
    )
)

REM Run database migrations
echo Running database migrations...
flask db upgrade
if %ERRORLEVEL% neq 0 (
    echo Error: Database migration failed
    exit /b 1
)

echo Starting Flask application...
python run.py

REM Deactivate virtual environment on exit
deactivate 