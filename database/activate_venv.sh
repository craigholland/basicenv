#!/usr/bin/env bash
#  USAGE: . ./activate_venv.sh

module="database"
venv_loc="/$module/.venv/bin"
module_loc="/$module"
pwds="$(pwd)"

if [[ "$PATH" =~ $venv_loc ]]; then
  echo "venv already activated"

elif [[ "$pwds" =~ $module_loc ]]; then
  echo "activating '$module' venv"
  curr_loc=$(echo "$pwds" | rev | awk -F "/" 'END {print $1}' | rev)
  while [ "$curr_loc" != "$module" ]; do
    pwds="${pwds%"/$curr_loc"}"
    curr_loc=$(echo "$pwds" | rev | awk -F "/" 'END {print $1}' | rev)
  done
  pwds="${pwds%"/$curr_loc"}$venv_loc"
  eval "source $pwds/activate"

else
  echo "Error in activating venv"
fi
