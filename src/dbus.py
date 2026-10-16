from pathlib import Path
from asyncio.exceptions import CancelledError

from kivy.app import App
from kivy.logger import Logger
from dbus_next import Variant
from dbus_next.aio import MessageBus
from dbus_next.service import (dbus_property, method, PropertyAccess as pa,
                               ServiceInterface, signal)

SHUFFLE = False


class MainInterface(ServiceInterface):
    def __init__(self):
        super().__init__("org.mpris.MediaPlayer2")

    # @method()
    # def Raise(self):
    #     pass

    # @method()
    # def Quit(self):
    #     pass

    @dbus_property(pa.READ)
    def CanQuit(self) -> "b":
        return False

    # @dbus_property()
    # def Fullscreen(self) -> "b":
    #     pass

    # @Fullscreen.setter
    # def Fullscreen(self, state: "b"):
    #     pass

    @dbus_property(pa.READ)
    def CanSetFullscreen(self) -> "b":
        return False

    @dbus_property(pa.READ)
    def HasTrackList(self) -> "b":
        return False

    @dbus_property(pa.READ)
    def Identity(self) -> "s":
        return "smpl"

    # should be in /usr/share/applications
    @dbus_property(pa.READ)
    def DesktopEntry(self) -> "s":
        return "smpl"

    # @dbus_property(pa.READ)
    # def SupportedUriSchemes(self) -> "as":
    #     return []

    # @dbus_property(pa.READ)
    # def SupportedMimeTypes(self) -> "as":
    #     return []

class PlayerInterface(ServiceInterface):
    def __init__(self):
        super().__init__("org.mpris.MediaPlayer2.Player")

    @method()
    def Next(self):
        player = App.get_running_app().player
        if player is not None:
            player.ids.next_button.play_next()

    @method()
    def Previous(self):
        player = App.get_running_app().player
        if player is not None:
            player.ids.previous_button.play_previous()

    @method()
    def Pause(self):
        player = App.get_running_app().player
        if player is not None:
            player.pause()

    @method()
    def PlayPause(self):
        player = App.get_running_app().player
        if player is not None:
            player.ids.play_button.toggle_play()

    @method()
    def Stop(self):
        player = App.get_running_app().player
        if player is not None:
            player.stop()

    @method()
    def Seek(self, offset: "x"):
        app = App.get_running_app()
        player = app.player
        Logger.info("BOOM offset")
        if player is not None:
            offset /= 10**6
            if offset < 0:
                time_to_seek = player.handler_track_pos(player.track_pos - offset)
                player.sound_provider.seek(time_to_seek)
                app.pause_pos = time_to_seek
                player.update_slider_value()
                player.update_pos()
            else:
                time_to_seek = player.handler_track_pos(player.track_pos + offset)
                player.sound_provider.seek(time_to_seek)
                app.pause_pos = time_to_seek
                player.update_slider_value()
                player.update_pos()
                self.Seeked(time_to_seek)

    @method()
    def SetPosition(self, trackid: "o", pos: "x"):
        app = App.get_running_app()
        player = app.player
        Logger.info("BOOM")
        if player is not None:
            if trackid != f"/org/mpris/MediaPlayer2/playlist/{player.now_playing.id}":
                return
            else:
                pos /= 10**6
                time_to_seek = player.handler_track_pos(pos)
                player.sound_provider.seek(time_to_seek)
                app.pause_pos = time_to_seek
                player.update_slider_value()
                player.update_pos()
                self.Seeked(time_to_seek)

    @signal()
    def Seeked(self, pos: "x") -> "x":
        Logger.info(f"Dbus: Seeked signal sent with {pos}")
        pos = pos * 10**6
        return int(pos)

    # May be "Playing", "Paused" or "Stopped".
    @dbus_property(pa.READ)
    def PlaybackStatus(self) -> "s":
        player = App.get_running_app().player
        if player is not None:
            state = player.sound_provider.state
            if state == "stop":
                return "Paused"
            else:
                return "Playing"
        return "Paused"

    @dbus_property()
    def LoopStatus(self) -> "s":
        app = App.get_running_app()
        if app.repeat == app.repeat_variants["no_repeat"]:
            value = "None"
        elif app.repeat == app.repeat_variants["repeat"]:
            value = "Track"
        elif app.repeat == app.repeat_variants["repeat_queue"]:
            value = "Playlist"
        return value

    @LoopStatus.setter
    def LoopStatus(self, value: "s"):
        app = App.get_running_app()
        if value == "None":
            app.repeat = app.repeat_variants["no_repeat"]
        elif value == "Track":
            app.repeat = app.repeat_variants["repeat"]
        elif value == "Playlist":
            app.repeat = app.repeat_variants["repeat_queue"]
        self.emit_properties_changed({'LoopStatus': value})

    @dbus_property()
    def Rate(self) -> "d":
        return 1.0

    @Rate.setter
    def Rate(self, value: "d"):
        # self.emit_properties_changed({'Rate': 1.0})
        pass

    @dbus_property(pa.READ)
    def MinimumRate(self) -> "d":
        return 1.0

    @dbus_property(pa.READ)
    def MaximunRate(self) -> "d":
        return 1.0

    @dbus_property()
    def Shuffle(self) -> "b":
        return SHUFFLE

    @Shuffle.setter
    def Shuffle(self, value: "b"):
        SHUFFLE = False
        self.emit_properties_changed({'Shuffle': False})

    def create_dbus_metadata(self, song):
        metadata = {
                "mpris:trackid": Variant("o", f"/org/mpris/MediaPlayer2/playlist/{song.id}"),
                "mpris:length": Variant("x", int(song.length * 10**6)),
                "mpris:artUrl": Variant("s", Path(song.image).as_uri()),
                "xesam:albumArtist": Variant("as", [song.artist]),
                "xesam:artist": Variant("as", [song.artist]),
                "xesam:album": Variant("s", song.album),
                "xesam:title": Variant("s", song.title),
                "xesam:url": Variant("s", Path(song.file).as_uri()),
                "xesam:trackNumber": Variant("i", song.album_pos),
                "xesam:contentCreated": Variant("s", song.year)
                }
        return metadata

    @dbus_property(pa.READ)
    def Metadata(self) -> "a{sv}":
        player = App.get_running_app().player
        if player is not None:
            song = player.now_playing
            metadata = self.create_dbus_metadata(song)
            return metadata
        return {"mpris:trackid": Variant("o", "/org/mpris/MediaPlayer2/TrackList/NoTrack")}

    @dbus_property()
    def Volume(self) -> "d":
        app = App.get_running_app()
        return app.volume

    @Volume.setter
    def Volume(self, value: "d"):
        app = App.get_running_app()
        if value < 0:
            value = 0
            app.volume = value
        self.emit_properties_changed({"Volume": value})

    @dbus_property(pa.READ)
    def Position(self) -> "x":
        player = App.get_running_app().player
        if player is not None:
            return int(player.track_pos) * 10**6
        else:
            return 0

    @dbus_property(pa.READ)
    def CanGoNext(self) -> "b":
        return True

    @dbus_property(pa.READ)
    def CanGoPrevious(self) -> "b":
        return True

    @dbus_property(pa.READ)
    def CanPlay(self) -> "b":
        return True

    @dbus_property(pa.READ)
    def CanPause(self) -> "b":
        return True

    @dbus_property(pa.READ)
    def CanSeek(self) -> "b":
        return True

    @dbus_property(pa.READ)
    def CanContol(self) -> "b":
        return True


player_interface = PlayerInterface()


async def start_dbus():
    bus_path = "/org/mpris/MediaPlayer2"
    bus_name = "org.mpris.MediaPlayer2.smpl"
    bus = await MessageBus().connect()
    main_interface = MainInterface()
    # player_interface = PlayerInterface()
    bus.export(bus_path, main_interface)
    bus.export(bus_path, player_interface)
    await bus.request_name(bus_name)
    Logger.info("Dbus: Ready")
    try:
        await bus.wait_for_disconnect()
    except CancelledError:
        Logger.info("Dbus: Stopped")
