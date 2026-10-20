@echo off
rem Lane AB: builds RDP's three native modules (_fastlm, _hamming, _span_hamming_fast) in place with MSVC, using
rem RDP's own setup.py (it already carries the MSVC flags /O2 /EHsc /std:c++20 /DNDEBUG). Run from anywhere:
rem     cmd //c agents\laneAB_rdp_port\build_native.bat [port dir, default dl\rdp_port]
rem Build outputs (.pyd, build\) stay inside the port copy; nothing is installed.
setlocal
set "HERE=%~dp0"
set "REPO=%HERE%..\.."
for %%I in ("%REPO%") do set "REPO=%%~fI"
set "PORT=%~1"
if "%PORT%"=="" set "PORT=dl\rdp_port"
for %%I in ("%REPO%\%PORT%") do set "PORT=%%~fI"
set "PY=%REPO%\dl\rdp_venv\Scripts\python.exe"
if not exist "%PORT%\setup.py" (
  echo missing %PORT%\setup.py - run setup_port.sh first
  exit /b 2
)
if not exist "%PY%" (
  echo missing %PY% - run setup_port.sh first
  exit /b 2
)
call "C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul
if errorlevel 1 (
  echo vcvars64.bat failed
  exit /b 1
)
set DISTUTILS_USE_SDK=1
set MSSdk=1
pushd "%PORT%"
"%PY%" setup.py -q build_ext --inplace
set "RC=%errorlevel%"
popd
if not "%RC%"=="0" (
  echo build_ext failed with %RC%
  exit /b %RC%
)
echo built native modules in "%PORT%\src\rdp\scoring"
