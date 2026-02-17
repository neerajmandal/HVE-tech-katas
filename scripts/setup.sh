#!/usr/bin/env bash
set -euo pipefail

SCRIPT_PATH="$(dirname "$(readlink -f "$0")")"
source "${SCRIPT_PATH}/common.sh"

###
### main execution path
###

print_stage "Extracting sample data archive..."
mkdir -p "${WORKSPACE_ROOT}/data"
if [ ! -f "${WORKSPACE_ROOT}/data/10-patients.zip" ]; then
  curl -L -O --output-dir "${WORKSPACE_ROOT}/data" https://github.com/smart-on-fhir/sample-bulk-fhir-datasets/archive/refs/heads/10-patients.zip
fi

print_stage "Setting up Python environment..."
uv sync

print_stage "Setting up Node environment..."
npm install

print_stage "Setting up Django..."
print_step "Compiling Tailwind CSS..."
npx @tailwindcss/cli -i static/input.css -o static/output.css --config tailwind.config.js

print_step "Collecting static files..."
uv run python manage.py collectstatic --noinput

print_step "Running database migrations..."
uv run python manage.py migrate
