export CONDA_EMSDK_DIR=$CONDA_PREFIX/lib/python$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")/site-packages/emsdk

export EMSDK_ENV="${CONDA_EMSDK_DIR}/emsdk_env.sh"

echo "Checking emsdk_env.sh..."
# Check if emsdk_env.sh exists
if [ ! -f "$EMSDK_ENV" ]; then
  echo "Error: emsdk_env.sh not found at $EMSDK_ENV."
  exit 0
fi

echo "Sourcing Emscripten environment..."
# Source the environment script to set up PATH and other variables
source "$EMSDK_ENV"
