#!/usr/bin/env bash
set -euE

SCRIPT_PATH="$(dirname "$(readlink -f "$0")")"
source "${SCRIPT_PATH}/../scripts/common.sh"

###
### main execution path
###
print_stage "Devcontainer runtime ready"
print_step "Django app is available on forwarded port 8000"
print_step "Container desktop is available on forwarded port 6080"
print_step "Use the desktop password 'vscode' when the noVNC viewer prompts for it"
