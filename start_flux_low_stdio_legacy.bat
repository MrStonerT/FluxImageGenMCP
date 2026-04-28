@echo off
setlocal EnableExtensions

set "ROOT=%~dp0"
call :resolve_venv
if errorlevel 1 goto :end

call "%VENV_DIR%\Scripts\activate.bat"
cd /d "%ROOT%"

set "FLUX_MODE=low"
set "HF_HOME=B:\Pond\hf_cache"
set "HF_HUB_DISABLE_XET=1"

echo Starting LEGACY FLUX MCP server in LOW mode via stdio...
echo This path is for manual debugging, not the persistent Goose service.
echo Using venv: %VENV_DIR%
python -u "%ROOT%mcp_flux_server.py"

:end
echo.
pause
exit /b

:resolve_venv
for %%D in ("%ROOT%flux-env-cu" "%ROOT%flux-env312" "%ROOT%.venv" "%ROOT%venv" "%ROOT%flux-env" "%ROOT%flux-env311") do (
    if exist "%%~fD\Scripts\activate.bat" (
        set "VENV_DIR=%%~fD"
        exit /b 0
    )
)
echo No virtual environment was found.
echo Expected one of:
echo   %ROOT%flux-env-cu
echo   %ROOT%flux-env312
echo   %ROOT%.venv
echo   %ROOT%venv
echo   %ROOT%flux-env
echo   %ROOT%flux-env311
exit /b 1
