#!/usr/bin/env bash
set -euE

SCRIPT_PATH="$(dirname "$(readlink -f "$0")")"
source "${SCRIPT_PATH}/../scripts/common.sh"

###
### main execution path
###
node ./scripts/setup.mjs
