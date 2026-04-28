param(
    [ValidateSet("low", "fast", "high")]
    [string]$Mode = "low",
    [int]$Port = 8765,
    [string]$BindHost = "127.0.0.1",
    [switch]$OpenDashboard
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$RunDir = Join-Path $Root ".flux-service"
$PortTag = [string]$Port
$PidFile = Join-Path $RunDir "flux-service-$PortTag.pid"
$MetaFile = Join-Path $RunDir "flux-service-$PortTag.json"
$StdoutLog = Join-Path $RunDir "stdout-$PortTag.log"
$StderrLog = Join-Path $RunDir "stderr-$PortTag.log"
$McpPath = "/mcp"
$HealthUrl = "http://$BindHost`:$Port/health"
$StatusUrl = "http://$BindHost`:$Port/status"
$DashboardUrl = "http://$BindHost`:$Port/"
$EndpointUrl = "http://$BindHost`:$Port$McpPath"

function Resolve-VenvDir {
    $candidates = @(
        "flux-env-cu",
        "flux-env312",
        ".venv",
        "venv",
        "flux-env",
        "flux-env311"
    )

    foreach ($name in $candidates) {
        $candidate = Join-Path $Root $name
        if (Test-Path (Join-Path $candidate "Scripts\python.exe")) {
            return $candidate
        }
    }

    throw "No virtual environment was found under $Root."
}

function Invoke-JsonOrNull {
    param([string]$Url)

    try {
        return Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec 5
    } catch {
        return $null
    }
}

function Get-FluxProcessFromPidFile {
    if (-not (Test-Path $PidFile)) {
        return $null
    }

    $raw = (Get-Content $PidFile -Raw).Trim()
    if ($raw -notmatch "^\d+$") {
        return $null
    }

    return Get-Process -Id ([int]$raw) -ErrorAction SilentlyContinue
}

function Get-ListenerOnPort {
    try {
        return Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    } catch {
        return $null
    }
}

if (-not (Test-Path $RunDir)) {
    New-Item -ItemType Directory -Path $RunDir | Out-Null
}

$existingHealth = Invoke-JsonOrNull -Url $HealthUrl
if ($existingHealth -and $existingHealth.ok) {
    Write-Host "FLUX service is already running."
    Write-Host "Mode: $($existingHealth.mode)"
    Write-Host "Endpoint: $($existingHealth.mcp_endpoint)"
    Write-Host "Dashboard: $DashboardUrl"
    if ($OpenDashboard) {
        Start-Process $DashboardUrl | Out-Null
    }
    exit 0
}

$listener = Get-ListenerOnPort
if ($listener) {
    throw "Port $Port is already in use, but it does not look like the FLUX service is healthy at $HealthUrl."
}

$venvDir = Resolve-VenvDir
$pythonExe = Join-Path $venvDir "Scripts\python.exe"

Set-Content -Path $StdoutLog -Value ""
Set-Content -Path $StderrLog -Value ""

$env:FLUX_MODE = $Mode
$env:HF_HOME = "B:\Pond\hf_cache"
$env:HF_HUB_DISABLE_XET = "1"
$env:FLUX_HTTP_HOST = $BindHost
$env:FLUX_HTTP_PORT = [string]$Port
$env:FLUX_HTTP_PATH = $McpPath

$args = @(
    "-u",
    (Join-Path $Root "mcp_flux_server.py"),
    "--transport", "streamable-http",
    "--host", $BindHost,
    "--port", [string]$Port,
    "--streamable-http-path", $McpPath
)

$proc = Start-Process `
    -FilePath $pythonExe `
    -ArgumentList $args `
    -WorkingDirectory $Root `
    -RedirectStandardOutput $StdoutLog `
    -RedirectStandardError $StderrLog `
    -WindowStyle Hidden `
    -PassThru

Set-Content -Path $PidFile -Value ([string]$proc.Id)

$meta = [ordered]@{
    pid = $proc.Id
    launcher_pid = $proc.Id
    mode = $Mode
    host = $BindHost
    port = $Port
    endpoint = $EndpointUrl
    dashboard = $DashboardUrl
    started_at = (Get-Date).ToString("o")
    stdout_log = $StdoutLog
    stderr_log = $StderrLog
}
$meta | ConvertTo-Json | Set-Content -Path $MetaFile

Write-Host "Starting FLUX service..."
Write-Host "Mode: $Mode"
Write-Host "Endpoint: $EndpointUrl"
Write-Host "Dashboard: $DashboardUrl"
Write-Host "Logs: $StderrLog"

$deadline = (Get-Date).AddMinutes(15)
$lastLogLine = ""
while ((Get-Date) -lt $deadline) {
    Start-Sleep -Seconds 2

    if ($proc.HasExited) {
        $tail = ""
        if (Test-Path $StderrLog) {
            $tail = (Get-Content $StderrLog -Tail 40) -join [Environment]::NewLine
        }
        throw "FLUX service exited during startup.`n$tail"
    }

    $health = Invoke-JsonOrNull -Url $HealthUrl
    if ($health -and $health.ok) {
        $status = Invoke-JsonOrNull -Url $StatusUrl
        if ($status -and $status.process_id) {
            $meta.pid = $status.process_id
            $meta | ConvertTo-Json | Set-Content -Path $MetaFile
        }
        Write-Host "FLUX service is ready."
        if ($OpenDashboard) {
            Start-Process $DashboardUrl | Out-Null
        }
        exit 0
    }

    if (Test-Path $StderrLog) {
        $currentLogLine = ((Get-Content $StderrLog -Tail 1) | Select-Object -First 1)
        if ($currentLogLine -and $currentLogLine -ne $lastLogLine) {
            Write-Host $currentLogLine
            $lastLogLine = $currentLogLine
        }
    }
}

throw "Timed out waiting for FLUX service to become healthy at $HealthUrl."
