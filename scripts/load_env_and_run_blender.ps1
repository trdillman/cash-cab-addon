$ErrorActionPreference = "Stop"

param(
  [string]$EnvPath = ".env",
  [string]$BlenderExe = "blender"
)

function Import-DotEnv([string]$path) {
  if (!(Test-Path $path)) {
    Write-Host "[CashCab] No .env found at $path"
    return
  }
  Get-Content $path | ForEach-Object {
    $line = $_.Trim()
    if ($line.Length -eq 0) { return }
    if ($line.StartsWith("#")) { return }
    $idx = $line.IndexOf("=")
    if ($idx -lt 1) { return }
    $key = $line.Substring(0, $idx).Trim()
    $val = $line.Substring($idx + 1).Trim()
    if ($val.StartsWith('\"') -and $val.EndsWith('\"')) { $val = $val.Substring(1, $val.Length - 2) }
    if ($val.StartsWith(\"'\") -and $val.EndsWith(\"'\")) { $val = $val.Substring(1, $val.Length - 2) }
    if ($key.Length -gt 0) {
      Set-Item -Path (\"Env:$key\") -Value $val
    }
  }
  Write-Host "[CashCab] Loaded env vars from $path"
}

Import-DotEnv $EnvPath

Write-Host "[CashCab] CASHCAB_GOOGLE_API_KEY set:" ([bool]$env:CASHCAB_GOOGLE_API_KEY)

# Launch Blender inheriting this process environment.
& $BlenderExe
