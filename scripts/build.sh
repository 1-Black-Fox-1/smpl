#!/bin/bash

# Rename if you have different venv dir name
VENV="venv"
SCRIPT_DIR="`dirname \"$0\"`"
# Change if your venv in another place
VENV_DIR="${SCRIPT_DIR}/../src/${VENV}"

VENV_ACTIVATED=false
if [ "$VIRTUAL_ENV" == "" ]; then
    VENV_ACTIVATED=true
    source "${VENV_DIR}/bin/activate"
fi

pyinstaller "${SCRIPT_DIR}/../src/main.py"\
    --distpath "${SCRIPT_DIR}/../bin"\
    --workpath "${SCRIPT_DIR}/../build"\
    --specpath "${SCRIPT_DIR}/.."\
    --name "smpl"\
    --add-data "${SCRIPT_DIR}/../src/resources/fonts:./resources/fonts"\
    --add-data "${SCRIPT_DIR}/../src/resources/images/:./resources/images"\
    --add-data "${SCRIPT_DIR}/../src/simpleplayer.kv:."\
    --hidden-import "main"\
    --onefile\
    #only for mac and win
    # --icon="${SCRIPT_DIR}../resources/images/simple-player.png"

if [ $VENV_ACTIVATED ]; then
    deactivate
    VENV_ACTIVATED=false
fi
