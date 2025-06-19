#!/bin/bash
# emsdk_setup.sh

# Path to emsdk_env.sh in the Pixi environment
EMSDK_ENV="${CONDA_EMSDK_DIR}/emsdk_env.sh"

echo "Checking emsdk_env.sh..."
# Check if emsdk_env.sh exists
if [ ! -f "$EMSDK_ENV" ]; then
  echo "Error: emsdk_env.sh not found at $EMSDK_ENV."
  exit 1
fi

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