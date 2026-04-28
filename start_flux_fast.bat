@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0start_flux_service.ps1" -Mode fast %*
