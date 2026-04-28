@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0stop_flux_service.ps1" %*
