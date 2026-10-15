#!/bin/bash

#TODO: edit venv varibles from flags
#TODO: handle errors

# Rename if you have different venv dir name
VENV="venv"
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
# Change if your venv in another place
VENV_DIR="${SCRIPT_DIR}/../src/${VENV}"

VENV_ACTIVATED=false
if [ "$VIRTUAL_ENV" == "" ]; then
    VENV_ACTIVATED=true
    source "${VENV_DIR}/bin/activate"
fi

while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help)
      echo "smpl build.sh - build your smpl from scratch"
      echo " "
      echo "build.sh [options]"
      echo " "
      echo "options:"
      echo "-h, --help                show brief help"
      echo "--no-async                build with no async support. Effects mpris"
      echo "--no-clean                dont clear build files"
      exit 0
      ;;
    --no-async)
        ASYNC=false
      shift
      ;;
    --no-clean)
        CLEAN=false
      shift
      ;;
    *)
      break
      ;;
  esac
done

if $ASYNC; then
    MAIN="${SCRIPT_DIR}/../src/asyncmain.py"
else
    MAIN="${SCRIPT_DIR}/../src/main.py"
fi

pyinstaller  ${MAIN} \
    --distpath "${SCRIPT_DIR}/../bin" \
    --workpath "${SCRIPT_DIR}/../build" \
    --specpath "${SCRIPT_DIR}" \
    --name "smpl" \
    --add-data "${SCRIPT_DIR}/../src/resources/fonts:./resources/fonts" \
    --add-data "${SCRIPT_DIR}/../src/resources/images/:./resources/images" \
    --add-data "${SCRIPT_DIR}/../src/simpleplayer.kv:." \
    --hidden-import "main" \
    --onefile \
    ${CLEAN:+--clean} \

if [ $VENV_ACTIVATED ]; then
    deactivate
    VENV_ACTIVATED=false
fi
