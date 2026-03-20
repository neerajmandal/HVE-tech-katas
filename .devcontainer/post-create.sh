#!/usr/bin/env bash
set -euE

SCRIPT_PATH="$(dirname "$(readlink -f "$0")")"
source "${SCRIPT_PATH}/../scripts/common.sh"

# Volume ownership is not set automatically due to a bug:
# https://github.com/microsoft/vscode-remote-release/issues/9931
#
# IMPORTANT: workaround requires Docker base image to have password-less sudo.
function fix_volume_ownership() {
  volume_path="$1"

  if [ ! -d "$volume_path" ]; then
    echo "ERROR: the volume path provided '$volume_path' does not exist."
    exit 1
  fi

  echo "Setting volume ownership for $volume_path"
  sudo chown $USER:$USER "$volume_path"
}

function fix_volume_ownerships() {
  print_stage "Applying volume ownership workaround (see microsoft/vscode-remote-release#9931)"
  fix_volume_ownership "/home/$USER/.azure"
  fix_volume_ownership "/home/$USER/.local"
  fix_volume_ownership "/home/$USER/.config"
  fix_volume_ownership "/workspace/.venv"
  fix_volume_ownership "/workspace/node_modules"
}

###
### main execution path
###

fix_volume_ownerships
