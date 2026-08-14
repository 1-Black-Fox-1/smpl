#!/bin/bash

# Rename if you have different venv dir name
VENV="venv"
SCRIPT_DIR="`dirname \"$0\"`"
VENV_DIR="${SCRIPT_DIR}/../${VENV}"

VENV_ACTIVATED=false
if [ "$VIRTUAL_ENV" == "" ]; then
    VENV_ACTIVATED=true
    source "${VENV_DIR}/bin/activate"
fi

pyinstaller "${SCRIPT_DIR}/../main.py"\
    --distpath "${SCRIPT_DIR}/../bin"\
    --workpath "${SCRIPT_DIR}"\
    --specpath "${SCRIPT_DIR}"\
    --name "smpl"\
    --add-data "${SCRIPT_DIR}/../resources/fonts:./resources/fonts"\
    --add-data "${SCRIPT_DIR}/../resources/images/:./resources/images"\
    --add-data "${SCRIPT_DIR}/../music:./music"\
    --add-data "${SCRIPT_DIR}/../simpleplayer.kv:."\
    --hidden-import "main"\
    --onefile\
    #only for mac and win
    # --icon="./images/simple-player.png"

if [ $VENV_ACTIVATED ]; then
    deactivate
    VENV_ACTIVATED=false
fi
