@echo off
echo Database Migration Manager

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Running initialization...
    call init.bat
    if %ERRORLEVEL% neq 0 (
        echo Error: Initialization failed
        exit /b 1
    )
)

REM Activate virtual environment
call venv\Scripts\activate.bat

:MENU
echo.
echo Database Management Options:
echo 1. Initialize migrations (first time setup)
echo 2. Create new migration
echo 3. Apply migrations
echo 4. Rollback last migration
echo 5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo Initializing database migrations...
    flask db init
    if %ERRORLEVEL% neq 0 (
        echo Error: Migration initialization failed
    ) else (
        echo Migration system initialized successfully!
    )
    goto :MENU
) else if "%choice%"=="2" (
    set /p msg="Enter migration message: "
    flask db migrate -m "%msg%"
    if %ERRORLEVEL% neq 0 (
        echo Error: Failed to create migration
    ) else (
        echo Migration created successfully!
    )
    goto :MENU
) else if "%choice%"=="3" (
    flask db upgrade
    if %ERRORLEVEL% neq 0 (
        echo Error: Failed to apply migrations
    ) else (
        echo Migrations applied successfully!
    )
    goto :MENU
) else if "%choice%"=="4" (
    flask db downgrade
    if %ERRORLEVEL% neq 0 (
        echo Error: Failed to rollback migration
    ) else (
        echo Migration rollback successful!
    )
    goto :MENU
) else if "%choice%"=="5" (
    goto :EOF
) else (
    echo Invalid choice!
    goto :MENU
)

REM Deactivate virtual environment on exit
deactivate 