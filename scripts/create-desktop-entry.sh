#!/usr/bin/bash
path=$HOME/.local/share/applications/SimplePlayer.desktop
echo -e "[Desktop Entry]
Exec=~/smpl/bin/Simple Player %f
Name=Simple Player
Icon=~/smpl/images/simple-player.png
Type=Application
Terminal=false"\
    > $path
chmod 700 $path
cat $path
echo "Created at $path"
