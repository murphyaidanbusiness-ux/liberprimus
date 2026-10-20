# Lane AB: run one command at BelowNormal priority with stdout to a log (stderr to <log>.err), with RDP's output root
# pinned inside the port copy. Waits for it (unless -NoWait) and exits with its exit code.
#   powershell -NoProfile -File agents/laneAB_rdp_port/run_bn.ps1 -Log agents/laneAB_rdp_port/logs/x.log `
#       -Cwd dl/rdp_port -Exe dl/rdp_venv/Scripts/python.exe -ArgLine "-m pytest -q tests/scoring"
param(
  [Parameter(Mandatory = $true)][string]$Log,
  [string]$Cwd = "dl/rdp_port",
  [Parameter(Mandatory = $true)][string]$Exe,
  [string]$ArgLine = "",
  [switch]$NoWait
)
$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$cwdAbs = (Resolve-Path (Join-Path $repo $Cwd)).Path
$logAbs = Join-Path $repo $Log
New-Item -ItemType Directory -Force (Split-Path $logAbs) | Out-Null
$out = Join-Path $repo "dl\rdp_port\output"
New-Item -ItemType Directory -Force $out | Out-Null
$env:RDP_OUTPUT_ROOT = $out
$env:PYTHONPATH = Join-Path $repo "dl\rdp_port\src"   # RDP is run from the port's source tree, never installed
$env:PYTHONUTF8 = "1"
$env:PYTHONDONTWRITEBYTECODE = "1"
if (-not [System.IO.Path]::IsPathRooted($Exe)) { $Exe = (Resolve-Path (Join-Path $repo $Exe)).Path }
$p = Start-Process -FilePath $Exe -ArgumentList $ArgLine -WorkingDirectory $cwdAbs -NoNewWindow -PassThru `
  -RedirectStandardOutput $logAbs -RedirectStandardError "$logAbs.err"
$null = $p.Handle   # keep the handle so ExitCode is available after WaitForExit
$p.PriorityClass = [System.Diagnostics.ProcessPriorityClass]::BelowNormal
Write-Output ("started pid {0} at {1} (BelowNormal): {2} {3}" -f $p.Id, (Get-Date -Format s), $Exe, $ArgLine)
if ($NoWait) { exit 0 }
$p.WaitForExit()
Write-Output ("exit {0} at {1}" -f $p.ExitCode, (Get-Date -Format s))
exit $p.ExitCode
