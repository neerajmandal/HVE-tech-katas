#!/bin/bash

SCRIPT_PATH="$(dirname "$(readlink -f "$0")")"
source "${SCRIPT_PATH}/common.sh"

###
### main execution path
###

print_stage "Starting web app for local development..."

# Activate the local virtual environment if available
if [ -f "${WORKSPACE_ROOT}/.venv/bin/activate" ]; then
  # POSIX (macOS / Linux / WSL)
  # shellcheck disable=SC1091
  source "${WORKSPACE_ROOT}/.venv/bin/activate"
elif [ -f "${WORKSPACE_ROOT}/.venv/Scripts/activate" ]; then
  # Git Bash on Windows
  # shellcheck disable=SC1091
  source "${WORKSPACE_ROOT}/.venv/Scripts/activate"
else
  echo "WARNING: .venv not found. Run 'npm run setup' first." >&2
fi

DEBUG=true python manage.py runserver
