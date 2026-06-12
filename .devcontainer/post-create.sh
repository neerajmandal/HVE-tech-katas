#!/usr/bin/env bash
set -euE

SCRIPT_PATH="$(dirname "$(readlink -f "$0")")"

# The repo hosts two self-contained kata apps under verticals/. The devcontainer
# provisions the healthcare baseline by default; switch DEFAULT_KATA to work the
# manufacturing kata (or any future vertical) instead.
DEFAULT_KATA="${STINGRAY_DEFAULT_KATA:-verticals/healthcare}"
KATA_ROOT="${SCRIPT_PATH}/../${DEFAULT_KATA}"
source "${KATA_ROOT}/scripts/common.sh"

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
  sudo chown -R "$USER:$USER" "$volume_path"
}

function fix_volume_ownerships() {
  print_stage "Applying volume ownership workaround (see microsoft/vscode-remote-release#9931)"
  fix_volume_ownership "/home/$USER/.azure"
  fix_volume_ownership "/home/$USER/.local"
  fix_volume_ownership "/home/$USER/.config"
  fix_volume_ownership "/home/$USER/.cache"
  fix_volume_ownership "/home/$USER/.cache/ms-playwright"
  fix_volume_ownership "/workspace/${DEFAULT_KATA}/.venv"
  fix_volume_ownership "/workspace/${DEFAULT_KATA}/node_modules"
}

###
### main execution path
###

fix_volume_ownerships

print_stage "Running one-time devcontainer provisioning"
cd "$WORKSPACE_ROOT"
npm run setup:devcontainer
