param(
    [int]$Port = 8765,
    [int]$Tail = 20
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$RunDir = Join-Path $Root ".flux-service"
$PortTag = [string]$Port
$MetaFile = Join-Path $RunDir "flux-service-$PortTag.json"
$StderrLog = Join-Path $RunDir "stderr-$PortTag.log"
$HealthUrl = "http://127.0.0.1:$Port/health"
$StatusUrl = "http://127.0.0.1:$Port/status"
$DashboardUrl = "http://127.0.0.1:$Port/"

function Invoke-JsonOrNull {
    param([string]$Url)

    try {
        return Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec 5
    } catch {
        return $null
    }
}

$meta = $null
if (Test-Path $MetaFile) {
    $meta = Get-Content $MetaFile -Raw | ConvertFrom-Json
}

$health = Invoke-JsonOrNull -Url $HealthUrl
$status = Invoke-JsonOrNull -Url $StatusUrl

Write-Host "Dashboard: $DashboardUrl"
Write-Host "Health: $HealthUrl"
Write-Host "Status: $StatusUrl"

if ($meta) {
    Write-Host "Recorded PID: $($meta.pid)"
    if ($meta.PSObject.Properties.Name -contains "launcher_pid" -and $meta.launcher_pid) {
        Write-Host "Launcher PID: $($meta.launcher_pid)"
    }
    Write-Host "Recorded mode: $($meta.mode)"
    Write-Host "Log file: $($meta.stderr_log)"
}

if ($health -and $health.ok) {
    Write-Host "Service state: healthy"
    Write-Host "MCP endpoint: $($health.mcp_endpoint)"
} else {
    Write-Host "Service state: unavailable"
}

if ($status) {
    Write-Host "Service PID: $($status.process_id)"
    Write-Host "Model: $($status.selected_model_id)"
    Write-Host "Transport: $($status.server_transport)"
    Write-Host "Load strategy: $($status.load_strategy)"
    Write-Host "GPU: $($status.gpu_name)"
    Write-Host "Generating: $($status.is_generating)"
    Write-Host "Images generated: $($status.total_images_generated)"
    Write-Host "Last generation seconds: $($status.last_generation_seconds)"
}

if ($Tail -gt 0 -and (Test-Path $StderrLog)) {
    Write-Host ""
    Write-Host "Recent log lines:"
    Get-Content $StderrLog -Tail $Tail
}
