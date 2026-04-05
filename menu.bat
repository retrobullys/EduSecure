@echo off
title EduSecure System Menu
color 0A

REM Change to the script's directory
cd /d "%~dp0"

:menu
cls
color 0A
echo ========================================
echo         EduSecure System Menu
echo ========================================
echo.
echo 1. Run Main Monitoring System
echo 2. Register Students
echo 3. Generate Reports
echo 4. Test Cheating Detection
echo 5. Install Dependencies
echo 6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto main
if "%choice%"=="2" goto register
if "%choice%"=="3" goto report
if "%choice%"=="4" goto test
if "%choice%"=="5" goto install
if "%choice%"=="6" goto exit

echo Invalid choice. Please try again.
pause
goto menu

:main
echo Starting EduSecure Main Monitoring System...
python main.py
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:register
echo Starting Student Registration...
python register_students.py
pause
goto menu

:report
echo Generating Reports...
python report.py
pause
goto menu

:test
echo Running Cheating Detection Tests...
python test_cheating.py
pause
goto menu

:install
echo Installing Dependencies...
echo Note: InsightFace may fail to install without Visual C++ Build Tools
echo.
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Some dependencies may have failed to install.
    echo The main monitoring system will still work with OpenCV fallback.
    echo Student registration requires InsightFace to be installed manually.
) else (
    echo.
    echo Dependencies installed successfully!
)
pause
goto menu

:exit
echo Thank you for using EduSecure!
pause
exit