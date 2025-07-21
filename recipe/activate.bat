@echo off

SET CONDA_EMSDK_DIR="%PREFIX%\lib\site-packages\emsdk"

set "EMSDK_ENV=%CONDA_EMSDK_DIR%\emsdk_env.bat"

if not exist "%EMSDK_ENV%" (
    echo [emsdk_setup] Error: "%EMSDK_ENV%" not found.
    echo               Is the 'emsdk' package installed in this environment?
    exit /b 0
)

echo [emsdk_setup] Activating Emscripten SDK from "%EMSDK_DIR%"
call "%EMSDK_ENV%"