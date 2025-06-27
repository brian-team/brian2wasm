:: emsdk_setup.bat - Windows version of emsdk setup

:: Path to emsdk_env.bat in the Pixi environment
set "EMSDK_ENV=%CONDA_EMSDK_DIR%\emsdk_env.bat"

echo Checking emsdk_env.bat...
:: Check if emsdk_env.bat exists
if not exist "%EMSDK_ENV%" (
  echo Error: emsdk_env.bat not found at %EMSDK_ENV%
  exit /b 1
)

echo Sourcing Emscripten environment...
:: Run the environment script to set up PATH and other variables
call "%EMSDK_ENV%"