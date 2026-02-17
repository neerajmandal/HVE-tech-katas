#!/bin/bash

SCRIPT_PATH="$(dirname "$(readlink -f "$0")")"
source "${SCRIPT_PATH}/common.sh"

###
### main execution path
###

print_stage "Starting web app for local development..."
DEBUG=true uv run python manage.py runserver