@echo off
:: -------------------------------------------------------------
:: emsdk_setup.bat  —  Activate Emscripten inside a Pixi/Conda env
:: Works in cmd.exe and inside PowerShell-run activation hooks.
:: -------------------------------------------------------------

:: 1. Make sure we are *inside* an activated env
if not defined CONDA_PREFIX (
    echo [emsdk_setup] Error: CONDA_PREFIX is not set. Activate the env first.
    exit /b 1
)

:: 2. Build the absolute path to emsdk_env.bat in site-packages
set "EMSDK_DIR=%CONDA_PREFIX%\Lib\site-packages\emsdk"
set "EMSDK_ENV=%EMSDK_DIR%\emsdk_env.bat"

if not exist "%EMSDK_ENV%" (
    echo [emsdk_setup] Error: "%EMSDK_ENV%" not found.
    echo               Is the 'emsdk' package installed in this environment?
    exit /b 1
)

:: 3. Call emsdk_env.bat (adds emcc, em++, node, and make to PATH)
echo [emsdk_setup] Activating Emscripten SDK from "%EMSDK_DIR%"
call "%EMSDK_ENV%"

:: 4. Optional sanity check — comment out if you don’t want the noise
where emcc >nul 2>&1
if errorlevel 1 (
    echo [emsdk_setup] Warning: emcc NOT on PATH after activation!
) else (
    echo [emsdk_setup] emcc is now on PATH.
)
