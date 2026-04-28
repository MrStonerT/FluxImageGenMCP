@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0monitor_flux_service.ps1" %*
