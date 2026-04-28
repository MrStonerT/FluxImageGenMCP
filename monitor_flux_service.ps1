param(
    [int]$Port = 8765,
    [int]$Tail = 30
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$RunDir = Join-Path $Root ".flux-service"
$PortTag = [string]$Port
$StderrLog = Join-Path $RunDir "stderr-$PortTag.log"
$DashboardUrl = "http://127.0.0.1:$Port/"
$StatusUrl = "http://127.0.0.1:$Port/status"

Write-Host "Dashboard: $DashboardUrl"
Write-Host "Status: $StatusUrl"
Write-Host "Tailing: $StderrLog"
Write-Host "Press Ctrl+C to stop monitoring."

if (-not (Test-Path $StderrLog)) {
    throw "Log file does not exist yet: $StderrLog"
}

Get-Content $StderrLog -Wait -Tail $Tail
