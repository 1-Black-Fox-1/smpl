#!/usr/bin/bash

DESKTOP_PATH=$HOME/.local/share/applications/simple-player.desktop
ICON_PATH=/usr/share/pixmaps/simple-player.png
BIN_PATH="$HOME/.local/bin/smpl"

rm $BIN_PATH
if [ $? -ne 0 ]; then
    exit
fi
echo "$BIN_PATH deleted"

rm $DESKTOP_PATH
if [ $? -ne 0 ]; then
    # echo "Can't create desktop file"
    exit
fi
echo "$DESKTOP_PATH deleted"

sudo rm $ICON_PATH
if [ $? -ne 0 ]; then
    # echo "Can't delete icon file"
    exit
fi
echo "$ICON_PATH deleted"
