#!/bin/bash
# emsdk_setup.sh

# Paths to emsdk and emsdk_env.sh in the Pixi environment
EMSDK_EXEC=".pixi/envs/default/bin/emsdk"
EMSDK_ENV=".pixi/envs/default/lib/python${PYTHON_VERSION:-3.13}/site-packages/emsdk/emsdk_env.sh"

echo "Checking emsdk executable..."
# Check if emsdk executable exists
if [ ! -f "$EMSDK_EXEC" ]; then
  echo "Error: emsdk executable not found at $EMSDK_EXEC."
  exit 1
fi

echo "Checking emsdk_env.sh..."
# Check if emsdk_env.sh exists
if [ ! -f "$EMSDK_ENV" ]; then
  echo "Error: emsdk_env.sh not found at $EMSDK_ENV."
  exit 1
fi

echo "Installing and activating latest Emscripten SDK..."
# Install and activate the latest Emscripten SDK
"$EMSDK_EXEC" install latest
"$EMSDK_EXEC" activate latest

echo "Sourcing Emscripten environment..."
# Source the environment script to set up PATH and other variables
source "$EMSDK_ENV"

echo "Verifying emcc..."
# Verify emcc is available
if command -v emcc >/dev/null 2>&1; then
  echo "emcc is available: $(emcc --version)"
else
  echo "Error: emcc not found in PATH after activation."
  exit 1
fi

echo "Verifying emrun..."
# Verify emrun is available
if command -v emrun >/dev/null 2>&1; then
  echo "emrun is available: $(emrun --version)"
else
  echo "Error: emrun not found in PATH after activation."
  exit 1
fi