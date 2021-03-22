#!/usr/bin/env bash
set -e

#### functions and tasks ##############################################################

function ensure_conda_env {
  local conda_env="mw_utils"
  local conda_run=conda

  if ! conda env list | awk '{print $1}' | grep -Fxq "$conda_env"; then
    echo "Installing environment: ${conda_env}"
    eval "$conda_run env create -f python/environment.yml -q"
  fi

  # see https://stackoverflow.com/a/56155771
  eval "$($conda_run shell.bash hook)" && conda activate "$conda_env"
  (cd python/ && python setup.py develop)
}

function format_python {
  if black python/ --check; then
    return
  fi

  read -p $'\nAre you sure you want to re-format (y/[n])? ' -n 1 -r
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo
    black python/
  else
    echo $'\nBlack reformatting aborted.'
  fi
}

function linting {
  shellcheck run.sh -x -e SC1091
  echo '========================================'
  echo 'Black check of python/:'
  format_python
  echo '========================================'
  echo 'Pylint python/scotch:'
  pylint python --rcfile python/pylintrc --ignore attic
  echo '========================================'
}

function unit_test_python {
  ensure_conda_env
  (cd python && pytest)
}

#### name tasks and task usage ########################################################
task_usage() {
  echo "Usage: ./run.sh lint | format | test | setup-conda"
  exit 1
}
cmd=$1
shift || true
case "$cmd" in
  lint) linting ;;
  format) format_python ;;
  test) unit_test_python ;;
  setup-conda) ensure_conda_env ;;
  *)     task_usage ;;
esac
