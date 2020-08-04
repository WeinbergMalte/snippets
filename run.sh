#!/usr/bin/env bash

set -e


#### Functions and tasks

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
  shellcheck bash/*.sh
  echo '========================================'
  echo 'Black check of python/:'
  format_python
  echo '========================================'
  echo 'Pylint python/scotch:'
  pylint python --rcfile python/pylintrc --ignore attic
  echo '========================================'
}


function unit_test_python {
  ensure_conda_environment
  (cd python && pytest)
}

#### name tasks and task usage ####
task_usage() {
  echo "Usage: ./run.sh lint | format | unit-test "
  exit 1
}

cmd=$1
shift || true
case "$cmd" in
  lint) linting ;;
  format) format_python ;;
  unit-test) unit_test_python ;;
  *)     task_usage ;;
esac
