@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo Select FLUX service mode:
echo   1. Fast / GGUF
echo   2. Low / base-4B
echo   3. High / dev
set /p FLUX_CHOICE=Enter 1, 2, or 3: 

if "%FLUX_CHOICE%"=="1" (
    call "%~dp0start_flux_fast.bat"
    exit /b
)

if "%FLUX_CHOICE%"=="2" (
    call "%~dp0start_flux_low.bat"
    exit /b
)

if "%FLUX_CHOICE%"=="3" (
    call "%~dp0start_flux_high.bat"
    exit /b
)

echo Invalid choice. Please run the launcher again and select 1, 2, or 3.
echo.
pause
