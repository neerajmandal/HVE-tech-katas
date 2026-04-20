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
  sudo chown -R "$USER:$USER" "$volume_path"
}

function fix_volume_ownerships() {
  print_stage "Applying volume ownership workaround (see microsoft/vscode-remote-release#9931)"
  fix_volume_ownership "/home/$USER/.azure"
  fix_volume_ownership "/home/$USER/.local"
  fix_volume_ownership "/home/$USER/.config"
  fix_volume_ownership "/home/$USER/.cache"
  fix_volume_ownership "/home/$USER/.cache/ms-playwright"
  fix_volume_ownership "/workspace/.venv"
  fix_volume_ownership "/workspace/node_modules"
}

function ensure_devcontainer_packages() {
  print_stage "Installing devcontainer system packages"

  if command -v shfmt > /dev/null 2>&1; then
    print_step "shfmt already installed"
    return
  fi

  print_step "Installing shfmt"
  sudo apt-get update
  sudo apt-get install -y shfmt
}

###
### main execution path
###

fix_volume_ownerships
ensure_devcontainer_packages

print_stage "Running one-time devcontainer provisioning"
cd "$WORKSPACE_ROOT"
npm run setup:devcontainer
