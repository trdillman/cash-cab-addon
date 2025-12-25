param(
  [int]$Port = 8811
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$server = Join-Path $scriptDir "claude-http-bridge.js"

Write-Host "Starting Claude HTTP bridge on 0.0.0.0:$Port ..."
Start-Process -FilePath "powershell" -ArgumentList @(
  "-NoProfile",
  "-WindowStyle",
  "Hidden",
  "-Command",
  "`$env:CLAUDE_BRIDGE_PORT=$Port; node `"$server`""
) -WorkingDirectory $scriptDir -WindowStyle Hidden | Out-Null
Start-Sleep -Milliseconds 300

try {
  $conn = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -First 1
  if (-not $conn) { throw "Bridge did not start (no listener on port $Port)." }
  Write-Host "Bridge started (PID $($conn.OwningProcess)). Health: http://localhost:$Port/health"
} catch {
  Write-Error $_
  exit 1
}
