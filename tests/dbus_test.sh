#!/bin/sh

# busctl --user call org.mpris.MediaPlayer2.smpl \
#     /org/mpris/MediaPlayer2 \
#     org.mpris.MediaPlayer2.Player \
#     Next

# busctl --user call org.mpris.MediaPlayer2.smpl \
#     /org/mpris/MediaPlayer2 \
#     org.mpris.MediaPlayer2.Player \
#     Previous

# busctl --user introspect org.mpris.MediaPlayer2.smpl \
#     /org/mpris/MediaPlayer2

# busctl --user get-property org.mpris.MediaPlayer2.smpl \
#     /org/mpris/MediaPlayer2 \
#     org.mpris.MediaPlayer2.Player \
#     Volume

# busctl --user get-property org.mpris.MediaPlayer2.vlc \
#     /org/mpris/MediaPlayer2 \
#     org.mpris.MediaPlayer2.Player \
#     Metadata

# busctl --user call org.mpris.MediaPlayer2.smpl \
#     /org/mpris/MediaPlayer2 \
#     org.mpris.MediaPlayer2.Player \
#     PlayPause

# dbus-monitor "sender='org.mpris.MediaPlayer2.smpl'"
