from kivy.app import App
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.core.window import Window
from winrt.windows.media import SystemMediaTransportControls, SystemMediaTransportControlsButtonPressedEventArgs, SystemMediaTransportControlsButton, MediaPlaybackType
from winrt.windows.media.interop import get_for_window
from winrt.windows.storage import StorageFile
from winrt.windows.storage.streams import RandomAccessStreamReference


hwnd = Window.get_window_info().window
controls = get_for_window(hwnd)


def on_media_button_pressed(sender: SystemMediaTransportControls,
                            args: SystemMediaTransportControlsButtonPressedEventArgs):
    Logger.info(f"Windows Media: Button pressed - {args.button.name}")
    match args.button:
        case SystemMediaTransportControlsButton.PLAY:
            player = App.get_running_app().player
            if player is not None:
                player.ids.play_button.toggle_play()
        case SystemMediaTransportControlsButton.PAUSE:
            player = App.get_running_app().player
            if player is not None:
                player.ids.play_button.toggle_play()
        case SystemMediaTransportControlsButton.NEXT:
            player = App.get_running_app().player
            if player is not None:
                Clock.schedule_once(lambda dt: player.ids.next_button.play_next(), 0)
        case SystemMediaTransportControlsButton.PREVIOUS:
            player = App.get_running_app().player
            if player is not None:
                Clock.schedule_once(lambda dt: player.ids.previous_button.play_previous(), 0)
        case _:
            Logger.warning(f"Windows Media: Unknown button {args.button.name}")


async def on_media_opened(sender, args):
    updater = controls.display_updater
    player = App.get_running_app().player
    updater.type = MediaPlaybackType.MUSIC
    updater.music_properties.album_title = player.now_playing.album
    # props.music_properties.album_track_count = player.now_playing.album_pos
    updater.music_properties.album_artist = player.now_playing.artist
    updater.music_properties.track_number = player.now_playing.album_pos
    updater.music_properties.title = player.now_playing.title
    updater.music_properties.artist = player.now_playing.artist
    image = player.now_playing.image
    image = await StorageFile.get_file_from_path_async(image)
    updater.thumbnail = RandomAccessStreamReference.create_from_file(image)
    updater.update()
    Logger.info(f"Windows Media: New media updated")
    enable_controls()


# def disable_controls(controls: SystemMediaTransportControls):
def disable_controls():
    controls.is_previous_enabled = False
    controls.is_next_enabled     = False
    controls.is_play_enabled     = False
    controls.is_pause_enabled    = False


# def enable_controls(controls: SystemMediaTransportControls):
def enable_controls():
    controls.is_previous_enabled = True
    controls.is_next_enabled     = True
    controls.is_play_enabled     = True
    controls.is_pause_enabled    = True


async def start_win_media():
    disable_controls()
    controls.add_button_pressed(on_media_button_pressed)
    Logger.info(f"Windows Media: Started")