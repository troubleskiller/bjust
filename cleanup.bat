@echo off
echo Cleaning up Python cache files...

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

echo.
echo Cleanup completed!
pause 