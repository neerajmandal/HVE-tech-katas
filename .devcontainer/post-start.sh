#!/usr/bin/env bash
set -euE

SCRIPT_PATH="$(dirname "$(readlink -f "$0")")"
DEFAULT_KATA="${STINGRAY_DEFAULT_KATA:-verticals/healthcare}"
source "${SCRIPT_PATH}/../${DEFAULT_KATA}/scripts/common.sh"

###
### main execution path
###
print_stage "Devcontainer runtime ready"
print_step "Django app is available on forwarded port 8000"
print_step "Container desktop is available on forwarded port 6080"
print_step "Use the desktop password 'password123' when the noVNC viewer prompts for it"
