#!/usr/bin/env bash

set -e


#### Functions and tasks


function make_symlink {
  local source=$1
  local destination=$2
  if [ -h "$destination" ]; then
    return 0
  elif [ -f "$destination" ]; then
    echo "File exists: ${destination}"
  else
    ln -sv "$(pwd)"/"$source" "$destination"
  fi
}

function task_setup_shell {
  make_symlink dotfiles/shell/bashrc ~/.bashrc
  make_symlink dotfiles/shell/bash_aliases ~/.bash_aliases
}

function task_setup_vim {
  # install neovim:
  sudo apt-get install neovim

  # vim and neovim dotfiles and color scheme
  mkdir -p ~/.config/nvim/colors
  cp dotfiles/vim/plugin/gruvbox.vim ~/.config/nvim/colors/
  make_symlink dotfiles/vim/vimrc ~/.vimrc
  make_symlink dotfiles/vim/vimrc ~/.config/nvim/init.vim
 }

function task_setup_vscode {
  sudo apt update
  sudo apt install software-properties-common apt-transport-https wget
  wget -q https://packages.microsoft.com/keys/microsoft.asc -O- | sudo apt-key add -
  sudo add-apt-repository "deb [arch=amd64] https://packages.microsoft.com/repos/vscode stable main"
  sudo apt update
  sudo apt install code
}

function ensure_conda_env {
  local conda_env="snippets"
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
  ensure_conda_environment
  (cd python && pytest)
}

#### name tasks and task usage ####
task_usage() {
  echo "Usage: ./run.sh lint | format | unit-test |
                setup-shell | setup-vim | setup-code | setup-conda"
  exit 1
}
cmd=$1
shift || true
case "$cmd" in
  lint) linting ;;
  format) format_python ;;
  unit-test) unit_test_python ;;
  setup-shell) task_setup_shell ;;
  setup-vim) task_setup_vim ;;
  setup-code) task_setup_vscode ;;
  setup-conda) ensure_conda_env ;;
  *)     task_usage ;;
esac
