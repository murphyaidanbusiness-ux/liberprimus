# Launch the zero-offset Quagmire-dodge priority sweep in the background at below-normal priority.
# Run from the repo root in PowerShell:
#   powershell -ExecutionPolicy Bypass -File agents\laneO_quagmire_dodge\launch_sweep.ps1 -NProc 8
#   powershell -ExecutionPolicy Bypass -File agents\laneO_quagmire_dodge\launch_sweep.ps1 -NProc 1 -Tasks 0 -Tag smoke1
# Tiers (see RESULTS.md section 8): -Tier A | B | C picks the word set; each tier has its own progress file.
# Resumable: rerun the same command and finished tasks (in out\<Tag>_progress.jsonl) are skipped.
# Stop it:  Get-CimInstance Win32_Process | ? CommandLine -match 'dodge_priority_sweep' | % { Stop-Process -Id $_.ProcessId }
# Workers are created by the parent, and Windows hands a BELOW_NORMAL parent's class to its children.
param([int]$NProc = 8, [string]$Tasks = "", [string]$Tag = "", [string]$Tier = "")

$TierA = "DIVINITY,FIRFUMFERENFE,CIRCUMFERENCE,PRIMES,PRIME,TOTIENT,INSTAR,PARABLE,KOAN,CICADA,LIBER,PRIMUS,WISDOM,PILGRIM"
$TierB = "WITHIN,TUNNELING,SURFACE,EMERGE,EMERGENCE,MOBIUS,MOEBIUS,SHADOW,ENLIGHTENMENT,CONSCIOUSNESS,INSTRUCTION,WELCOME,PATIENCE,DECEPTION,PRESERVATION,ADHERENCE,SACRED,TRUTH,SELF,REALITY,DIUINITY,CIRCUMFERENCES,AMASS,ANALOG,VOID,BUFFERS,PILGRIMAGE,PRIMALITY,SACRIFICE,SEEKER,STUDENT,MASTER,JOURNEY"
foreach ($v in @("DODGE_WORDS", "DODGE_EXCLUDE_WORDS", "DODGE_EXTRA_WORDS")) { Remove-Item "Env:$v" -ErrorAction SilentlyContinue }
$env:DODGE_EXTRA_WORDS = "FIRFUMFERENFE"
switch ($Tier) {
  "A" { $env:DODGE_WORDS = $TierA }
  "B" { $env:DODGE_WORDS = $TierB }
  "C" { $env:DODGE_EXCLUDE_WORDS = "$TierA,$TierB" }
  ""  { }
  default { throw "Tier must be A, B, C or empty (everything)" }
}
if (-not $Tag) { $Tag = if ($Tier) { "tier$Tier" } else { "full" } }

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path "$PSScriptRoot\..\..").Path
$lane = Join-Path $repo "agents\laneO_quagmire_dodge"
$py = (Get-Command python -ErrorAction Stop).Source
if ($py -match "WindowsApps") { throw "python resolves to the Store stub ($py); put the real interpreter first on PATH" }

$env:PYTHONUTF8 = "1"
$env:PYTHONPATH = Join-Path $repo "dl\aldegonde_port\src"
$env:DODGE_KERNEL_DLL = Join-Path $lane "build\dodge_score_kernel_m29.dll"
$env:DODGE_PROSE = Join-Path $repo "dl\dukotah\liber-primus\data\keys\armada18\melville_moby_dick.txt"
$env:DODGE_PROGRESS = Join-Path $lane "out\${Tag}_progress.jsonl"
$env:DODGE_OUT = Join-Path $lane "out\${Tag}_candidates.jsonl"
foreach ($f in @($env:DODGE_KERNEL_DLL, $env:DODGE_PROSE)) { if (-not (Test-Path $f)) { throw "missing $f" } }

$args = @("-u", "dl\aldegonde_port\experiments\dodge_priority_sweep.py", "--nproc", "$NProc")
if ($Tasks) { $args += @("--tasks", $Tasks) }
$log = Join-Path $lane "logs\${Tag}_sweep.log"
$p = Start-Process -FilePath $py -ArgumentList $args -WorkingDirectory $repo -NoNewWindow -PassThru `
        -RedirectStandardOutput $log -RedirectStandardError "$log.err"
$p.PriorityClass = "BelowNormal"
"started pid $($p.Id) at BelowNormal: $py $($args -join ' ')"
"log: $log   progress: $env:DODGE_PROGRESS"
