@echo off
rem Lane O: builds the dodge-aware score kernel (dl/aldegonde_port/experiments/dodge_score_kernel.c)
rem as a Windows DLL with MSVC. Paths are relative to this file, so it runs from any directory.
rem Output: agents\laneO_quagmire_dodge\build\dodge_score_kernel_m29.dll  (build artifact, not committed)
rem Load it with:  set DODGE_KERNEL_DLL=<that path>
setlocal
set "HERE=%~dp0"
set "REPO=%HERE%..\.."
for %%I in ("%REPO%") do set "REPO=%%~fI"
set "PORT=%REPO%\dl\aldegonde_port"
set "OUTDIR=%HERE%build"
if not exist "%OUTDIR%" mkdir "%OUTDIR%"
if not exist "%PORT%\experiments\dodge_score_kernel.c" (
  echo missing %PORT%\experiments\dodge_score_kernel.c - run setup_port.sh first
  exit /b 2
)
call "C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul
if errorlevel 1 (
  echo vcvars64.bat failed
  exit /b 1
)
pushd "%OUTDIR%"
cl /nologo /O2 /std:c11 /W3 /LD /DM=29 "%PORT%\experiments\dodge_score_kernel.c" /link /EXPORT:score_dials /OUT:"%OUTDIR%\dodge_score_kernel_m29.dll"
set "RC=%errorlevel%"
popd
if not "%RC%"=="0" (
  echo cl failed with %RC%
  exit /b %RC%
)
echo built "%OUTDIR%\dodge_score_kernel_m29.dll"
exit /b 0
