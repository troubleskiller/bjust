@echo off
echo WARNING: This script will delete all data and reset the project to initial state!
echo This includes:
echo - All Python cache files
echo - Instance folder
echo - Migrations folder
echo - Storage folder
echo - Virtual environment folder
echo.
echo Are you sure you want to continue? (Y/N)
set /p confirm=

if /i "%confirm%"=="Y" (
    echo.
    echo Starting cleanup process...
    
    REM Delete __pycache__ directories
    for /d /r . %%d in (__pycache__) do (
        if exist "%%d" (
            echo Removing: %%d
            rd /s /q "%%d"
        )
    )

    REM Delete all .pyc files
    for /r . %%f in (*.pyc) do (
        if exist "%%f" (
            echo Removing: %%f
            del /f /q "%%f"
        )
    )

    REM Delete instance folder
    if exist "instance" (
        echo Removing instance folder...
        rd /s /q "instance"
    )

    REM Delete migrations folder
    if exist "migrations" (
        echo Removing migrations folder...
        rd /s /q "migrations"
    )

    REM Delete storage folder
    if exist "storage" (
        echo Removing storage folder...
        rd /s /q "storage"
    )

    REM Delete virtual environment folder
    if exist "venv" (
        echo Removing virtual environment folder...
        rd /s /q "venv"
    )

    echo.
    echo Cleanup completed successfully!
    echo Project has been reset to initial state.
    echo Please run './start.bat' to initialize and start the project.
) else (
    echo.
    echo Cleanup cancelled.
)

pause 