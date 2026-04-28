param(
    [int]$Port = 8765
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$RunDir = Join-Path $Root ".flux-service"
$PortTag = [string]$Port
$PidFile = Join-Path $RunDir "flux-service-$PortTag.pid"
$MetaFile = Join-Path $RunDir "flux-service-$PortTag.json"
$HealthUrl = "http://127.0.0.1:$Port/health"

function Invoke-JsonOrNull {
    param([string]$Url)

    try {
        return Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec 5
    } catch {
        return $null
    }
}

function Get-FluxProcess {
    $processes = @()

    if (Test-Path $PidFile) {
        $raw = (Get-Content $PidFile -Raw).Trim()
        if ($raw -match "^\d+$") {
            $proc = Get-Process -Id ([int]$raw) -ErrorAction SilentlyContinue
            if ($proc) {
                $processes += $proc
            }
        }
    }

    $candidates = Get-CimInstance Win32_Process | Where-Object {
        $_.Name -eq "python.exe" -and
        $_.CommandLine -match "mcp_flux_server\.py" -and
        $_.CommandLine -match "--transport streamable-http" -and
        $_.CommandLine -match "--port $Port"
    }

    if ($candidates) {
        foreach ($candidate in $candidates) {
            $proc = Get-Process -Id $candidate.ProcessId -ErrorAction SilentlyContinue
            if ($proc) {
                $processes += $proc
            }
        }
    }

    return $processes | Sort-Object Id -Unique
}

$health = Invoke-JsonOrNull -Url $HealthUrl
$procs = @(Get-FluxProcess)

if (-not $procs -and -not $health) {
    Write-Host "No FLUX service process found on port $Port."
    exit 0
}

if ($procs) {
    $procs | Sort-Object Id -Descending | ForEach-Object {
        Stop-Process -Id $_.Id -Force
        Write-Host "Stopped FLUX service process $($_.Id)."
    }
    Start-Sleep -Seconds 1
}

if (Test-Path $PidFile) {
    Remove-Item -LiteralPath $PidFile -Force
}
if (Test-Path $MetaFile) {
    Remove-Item -LiteralPath $MetaFile -Force
}
