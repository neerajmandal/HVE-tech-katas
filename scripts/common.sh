#!/usr/bin/env bash
set -euE

# https://stackoverflow.com/a/53183593
SCRIPT_PATH="$(dirname -- "${BASH_SOURCE[0]}")"
SCRIPT_PATH="$(realpath -- "$SCRIPT_PATH")"
export WORKSPACE_ROOT="$(dirname "$SCRIPT_PATH")"
echo "Using workspace root: ${WORKSPACE_ROOT}"

print_stage() { echo -e "\n\n*** $@"; }
print_step() { echo -e "- $@"; }

function error_trap {
  lineno="$1"
  command="$2"
  exit_code="$3"
  script_path="${BASH_SOURCE[1]}"
  echo
  print_stage "ERROR: script failed to execute!"
  print_step "Error occurred at ${script_path}:${lineno}"
  print_step "Command being executed: $command"
  print_step "Command exit code was: $exit_code"
}

trap 'error_trap $LINENO "$BASH_COMMAND" $?' ERR

# Load environment variables from specified file (or .env), if exists
load_env_file() {
  env_file="${1:-$WORKSPACE_ROOT/.env}"
  print_stage "Loading env file: ${env_file}"

  if [ -f "$env_file" ]; then
    set -o allexport
    source "${env_file}"
    set +o allexport
  else
    echo "Failed to load environment configuration file '$env_file': file does not exist"
    exit 1
  fi
}
