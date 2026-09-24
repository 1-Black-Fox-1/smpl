#!/usr/bin/bash

DESKTOP_PATH=$HOME/.local/share/applications/simple-player.desktop
ICON_PATH=/usr/share/pixmaps/simple-player.png
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
BIN_PATH="$HOME/.local/bin/smpl"

cp "$SCRIPT_DIR/../bin/smpl" $BIN_PATH
if [ $? -ne 0 ]; then
    exit
fi
echo "Binary at $BIN_PATH"

echo -e "[Desktop Entry]
Exec=$HOME/.local/bin/smpl
Name=Simple Player
Icon=simple-player
Type=Application
Terminal=false
Keywords=smpl;"\
    > $DESKTOP_PATH
if [ $? -ne 0 ]; then
    # echo "Can't create desktop file"
    exit
fi

chmod 700 $DESKTOP_PATH
# cat $DESKTOP_PATH
echo "Created at $DESKTOP_PATH"

sudo cp $SCRIPT_DIR/../src/resources/images/simple-player.png $ICON_PATH
if [ $? -ne 0 ]; then
    # echo "Can't create icon"
    exit
fi
echo "Icon at $ICON_PATH"
