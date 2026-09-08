import kivy

kivy.require('2.3.1')

from json import dumps, loads
from pathlib import Path
from threading import Thread

from pynput import keyboard
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.logger import Logger
from kivy.graphics import Color, Rectangle
from kivy.properties import (BooleanProperty, BoundedNumericProperty,
                             DictProperty, ListProperty, NumericProperty,
                             ObjectProperty, StringProperty)
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.uix.spinner import Spinner
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import (CardTransition, NoTransition, Screen,
                                    ScreenManager, SlideTransition)
from kivy.uix.recycleview.views import RecycleKVIDsDataViewBehavior
from kivy.core.audio import SoundLoader
from kivy.core.window import Window

from db import create_db, db_exists, get_all, remove_db
from utils import application_path, get_cache_dir, tracks
from config import Color as Clr, Font, Size
from metadata import Metadata

__version__ = "1.0.0"

Config.set("input", "mouse", "mouse,multitouch_on_demand")

# TODO: better logging
# TODO: use outer audio engine, not kivy's?
# TODO: sync json one time at exit with all config data

# TODO: move it to utils
def formated_time(time: int|float) -> str:
    mins = int((time / 60))
    secs = int(time - mins * 60)
    return f"{mins}:{secs:02}"

# TODO: if audio device is disconnected stop music!

class Cover(Image):
    # TODO: tap on image to open it fullscreen
    cover_path = StringProperty()


class PlayButton(Button):
    # text = StringProperty('Play')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Clock.scedule_once(App.get_running_app().root.sound_provider.on_play =
        #                    self.on_press, -1)
        # Clock.scedule_once(App.get_running_app().root.sound_provider.on_stop =
        #                    self.on_press, -1)

    def toggle_play(self):
        root = App.get_running_app().root.get_screen("player")
        if root.sound_provider.state == "stop":
            save_pos = root.sound_provider.get_pos()
            root.sound_provider.play()
            Logger.info("Player: Start playing")
            Clock.schedule_once(lambda dt: root.sound_provider.seek(save_pos), 0)
            Logger.info(f"Player: Seek {save_pos}")
        else:
            root.sound_provider.stop()
            Logger.info("Player: Stop playing")

    def background_on_play(self, obj):
        self.background_down = f"{application_path}/resources/images/play_circle.png"
        self.background_normal = f"{application_path}/resources/images/pause_circle.png"

    def background_on_pause(self, obj):
        self.background_down = f"{application_path}/resources/images/play_circle.png"
        self.background_normal = f"{application_path}/resources/images/play_circle.png"


class PreviousButton(Button):
    def play_previous(self):
        root = App.get_running_app().root.get_screen("player")
        if root.track_pos > root.time_move_to_start or root.first_in_queue():
            root.sound_provider.seek(0)
        else:
            root._set_now_playing_pos(root.now_playing_pos - 1)


class NextButton(Button):
    def play_next(self):
        root = App.get_running_app().root.get_screen("player")
        root._set_now_playing_pos(root.now_playing_pos + 1)


class SeekForwardButton(Button):
    def on_press(self):
        root = App.get_running_app().root.get_screen("player")
        time_to_seek = root.handler_track_pos(root.track_pos + root.seek_time)
        root.sound_provider.seek(time_to_seek)
        root.update_slider_value()
        root.update_pos()


class SeekBackwardButton(Button):
    def on_press(self):
        root = App.get_running_app().root.get_screen("player")
        time_to_seek = root.handler_track_pos(root.track_pos - root.seek_time)
        root.sound_provider.seek(time_to_seek)
        root.update_slider_value()
        root.update_pos()


class QueueButton(Button):
    def open_queue(self):
        sm = App.get_running_app().root
        # FIXME: white transition
        sm.transition = CardTransition()
        sm.transition.direction = "up"
        sm.transition.mode = "push"
        sm.current = "queue"


class IconButton(ButtonBehavior, Image):
    def source_on_play(self, obj):
        pass
        self.source = f"{application_path}/resources/images/pause_circle.png"

    def source_on_pause(self, obj):
        self.source = f"{application_path}/resources/images/play_circle.png"

    def toggle_play(self):
        root = App.get_running_app().root.get_screen("player")
        if root.sound_provider.state == "stop":
            save_pos = root.sound_provider.get_pos()
            root.sound_provider.play()
            Logger.info("Player: Start playing")
            Clock.schedule_once(lambda dt: root.sound_provider.seek(save_pos), 0)
            Logger.info(f"Player: Seek {save_pos}")
        else:
            root.sound_provider.stop()
            Logger.info("Player: Stop playing")


class BackButton(Button):
    def go_back(self):
        root = App.get_running_app().root
        screen = root.current
        if screen == "settings":
            root.current = "library"
        elif screen == "player" or "queue":
            root.transition = SlideTransition()
            root.transition.direction = "down"
            root.current = "library"


class OptionsButton(Button):
    pass


# TODO: shuffle
class Options(Popup):
    pass


class RepeatSpinner(Spinner):
    repeat_variants = ListProperty(["Repeat", "No repeat", "Repeat queue"])


class VolumeSlider(Slider):
    def slider_move(self, touch, obj):
        # Logger.info(f'{touch}, {obj}')
        if touch.grab_current == obj:
            app = App.get_running_app()
            player = app.root.get_screen("player")
            app.volume = self.value
            player.sound_provider.volume = self.value
            # Logger.info(app.volume)

    def slider_up(self, touch, obj):
        # Logger.info(f'{touch}, {obj}')
        if touch.grab_current == obj:
            app = App.get_running_app()
            player = app.root.get_screen("player")
            app.volume = self.value
            player.sound_provider.volume = self.value
            # Logger.info(app.volume)


class TitleLabel(Label):
    text = StringProperty()


class ArtistLabel(Label):
    text = StringProperty()


class MusicSlider(Slider):
    value = NumericProperty()

    def slider_move(self, touch, obj):
        # Logger.info(f'{touch}, {obj}')
        if touch.grab_current == obj:
            root = App.get_running_app().root.get_screen("player")
            root.sound_provider.seek(self.value)
            root.track_pos = self.value

    def slider_up(self, touch, obj):
        # Logger.info(f'{touch}, {obj}')
        if touch.grab_current == obj:
            root = App.get_running_app().root.get_screen("player")
            root.sound_provider.seek(self.value)
            root.track_pos = self.value


class PosLabel(Label):
    text = StringProperty()


class LengthLabel(Label):
    text = StringProperty()


class PlayerScreen(Screen):

    queue = ListProperty(None)
    queue_length = NumericProperty(None)
    now_playing_pos = NumericProperty(None)
    now_playing = ObjectProperty(None)
    # sound_provider = ObjectProperty(SoundLoader.load(tracks[play_from]), rebind=True)
    sound_provider = ObjectProperty(rebind=True)
    # metadt = ObjectProperty(Metadata(tracks[play_from]), rebind=True)
    # metadts = ListProperty([Metadata(track) for track in tracks])
    # metadt = ObjectProperty()
    # metadts = ListProperty()
    slider_value = NumericProperty(0)
    track_pos = NumericProperty(0)
    length = NumericProperty(0)
    launched = False
    # TODO: set up it in settings
    time_move_to_start = NumericProperty(5)

    def __init__(self, queue, pos=0, **kwargs):
        super().__init__(**kwargs)
        # TODO: set up player seek time in settings
        self.seek_time = 10
        update_pos_frequency = 1 / 5
        self.update_pos_event = Clock.schedule_interval(lambda dt: self.update_pos(),
                                                        update_pos_frequency)
        self.update_pos_event.cancel()
        update_slider_frequency = 1
        self.update_slider_value_event = Clock.schedule_interval(lambda dt:
                                                                 self.update_slider_value(),
                                                                 update_slider_frequency)
        self.update_slider_value_event.cancel()

        self.keyboard_listener = Thread(target=self.keyboard_listener_setup,
                                        daemon=True)
        self.keyboard_listener.start()
        Clock.schedule_once(lambda dt: self.update_queue_and_now_pos(queue, pos), -1)
        # Should be in lib player
        self.update_lib_pos_event = Clock.schedule_interval(lambda dt:
                                                            self.update_lib_pos_value(),
                                                            update_slider_frequency)
        Clock.schedule_once(lambda dt:
                            self.update_lib_pos_event.cancel(),
                            update_slider_frequency)

    def stop_and_delete(self):
        self.sound_provider.stop()
        self.sound_proveder.unload()

    def update_lib_pos_value(self):
        app = App.get_running_app()
        app.lib_player.track_pos = f"{formated_time(app.player.track_pos)}/{formated_time(app.player.now_playing.length)}"

    def update_queue_and_now_pos(self, queue, pos=0):
        self.queue = queue
        self.now_playing_pos = pos

    def keyboard_listener_setup(self):
        def on_release(key):
            root = App.get_running_app().root.get_screen("player")
            if key == keyboard.Key.media_play_pause:
                Clock.schedule_once(lambda dt:
                                    root.ids.play_button.toggle_play())
                Logger.info(key)
            elif key == keyboard.Key.media_next:
                Clock.schedule_once(lambda dt:
                                    root.ids.next_button.play_next())
                Logger.info(key)
            elif key == keyboard.Key.media_previous:
                Clock.schedule_once(lambda dt:
                                    root.ids.previous_button.play_previous())
                Logger.info(key)

        with keyboard.Listener(on_release=on_release) as listener:
            listener.join()

    def set_length(self):
        self.length = self.sound_provider.length

    def update_pos(self):
        self.track_pos = self.sound_provider.get_pos()

    def update_slider_value(self):
        self.slider_value = self.sound_provider.get_pos()

    def on_queue(self, obj, value):
        self.queue_length = len(self.queue)
        Logger.info(f"length: {self.queue_length}")

    def on_now_playing_pos(self, obj, value):
        self.now_playing = self.queue[self.now_playing_pos]
        if self.sound_provider is not None:
            prev_track_state = self.sound_provider.state
            prev_track_loop = self.sound_provider.loop
            if prev_track_state == "play":
                self.sound_provider.stop()
            self.sound_provider.unload()
        else:
            prev_track_state = None
            prev_track_loop = None
        self.sound_provider = SoundLoader.load(self.now_playing.file)
        Logger.info(f"Player: New song {self.now_playing.title}")
        self.set_length()
        self.bind_play_button()
        self.bind_update_pos()
        self.sound_provider.bind(on_stop=self.auto_play_next)
        app = App.get_running_app()
        self.sound_provider.volume = app.volume
        if prev_track_loop is not None:
            self.sound_provider.loop = prev_track_loop
        if prev_track_state == "play":
            self.sound_provider.play()
        root = app.root
        screen = root.current
        root.get_screen(screen).update_hl()
        if not self.launched:
            Clock.schedule_once(lambda dt: self.bind_play_button(), -1)
            Clock.schedule_once(lambda dt: self.bind_update_pos(), -1)
            Clock.schedule_once(lambda dt:
                                self.sound_provider.bind(on_stop=self.auto_play_next), -1)
            Clock.schedule_once(lambda dt: self.set_length(), -1)
            self.launched = True

    def bind_play_button(self):
        sm = App.get_running_app().root
        player = sm.get_screen("player")
        # if player.sound_provider is not None:
        player.sound_provider.bind(on_play=player.ids.play_button.background_on_play)
        player.sound_provider.bind(on_stop=player.ids.play_button.background_on_pause)
        # Should be in lib player actually
        Clock.schedule_once(lambda dt: bind_lib_player(), -1)

        def bind_lib_player():
            app = App.get_running_app()
            player.sound_provider.bind(on_play=app.lib_player.ids.lib_play_button.source_on_play)
            player.sound_provider.bind(on_stop=app.lib_player.ids.lib_play_button.source_on_pause)

    def first_in_queue(self) -> bool:
        if self.now_playing_pos == 0:
            return True
        return False

    def last_in_queue(self) -> bool:
        if self.queue_length - 1 == self.now_playing_pos:
            return True
        return False

    # do not know how to name it
    def auto_play_next(self, obj):
        app = App.get_running_app()
        root = app.root.get_screen("player")
        if abs(self.track_pos - self.length) < 0.5:
            if (self.last_in_queue() and app.repeat == app.repeat_variants["repeat_queue"]):
                root._set_now_playing_pos(0)
                Clock.schedule_once(lambda dt: root.sound_provider.play(), 0)
                return
        if self.last_in_queue():
            return
        # Logger.info('Auto play next tried')
        # Logger.info(f'{round(self.track_pos)} == {round(self.length)}')
        # Logger.info(f'{(self.track_pos)} == {(self.length)}')
        # Logger.info(abs(self.track_pos - self.length))
        # there is math.ceil() to round UP to int
        if abs(self.track_pos - self.length) < 0.5:
            Logger.info('Auto play next succeded')
            root._set_now_playing_pos(root.now_playing_pos + 1)
            Clock.schedule_once(lambda dt: root.sound_provider.play(), 0)

    def bind_update_pos(self):
        Logger.info('staring binding events')
        # if self.sound_provider is not None:
        self.sound_provider.bind(on_play=self.start_time_events)
        self.sound_provider.bind(on_stop=self.stop_time_events)

    def stop_time_events(self, obj):
        Logger.info('stop_events')
        self.update_slider_value_event.cancel()
        self.update_pos_event.cancel()
        self.update_lib_pos_event.cancel()

    def start_time_events(self, obj):
        Logger.info('start_events')
        self.update_slider_value_event()
        self.update_pos_event()
        self.update_lib_pos_event()

    # TODO: remove _ and add it to handlers
    def _set_now_playing_pos(self, value):
        self.now_playing_pos = self.handler_now_playing_pos(value)

    def handler_now_playing_pos(self, value):
        if value < 0:
            return 0
        if value >= self.queue_length:
            return self.queue_length - 1
        return value

    def handler_track_pos(self, value):
        if value < 0:
            return 0
        if value > self.sound_provider.length:
            return self.sound_provider.length
        return value


class TrackView(RecycleKVIDsDataViewBehavior, BoxLayout, Button):
    now_playing = BooleanProperty(False)
    index = NumericProperty()
    k = 0
    def play_track(self):
        app = App.get_running_app()
        screen = app.root.current
        if screen == "queue":
            player = app.root.get_screen("player")
            if not self.now_playing:
                player._set_now_playing_pos(self.index)
        elif screen == "library":
            library = app.root.get_screen("library")
            try:
                library.ids.lib_box.remove_widget(app.lib_player)
                app.root.remove_widget(app.player)
            except AttributeError:
                pass
            queue = [app.songs[self.index]]
            # We are leaking here or something
            # Need to create one instance and then update it??
            if self.k > 1:
                app.player.stop_and_delete()
            self.k += 1
            app.player = PlayerScreen(name="player", queue=queue)
            app.root.add_widget(app.player)

            def create_lib_player():
                app = App.get_running_app()
                library = app.root.get_screen("library")
                lib_player = LibraryPlayer()
                app.lib_player = lib_player
                library.ids.lib_box.add_widget(lib_player)

            Clock.schedule_once(lambda dt: create_lib_player(), -1)
            Clock.schedule_once(lambda dt: app.player.sound_provider.play(), -1)

            # if app.lib_player is None:
            #     lib_player = LibraryPlayer()
            #     app.lib_player = lib_player
            #     library.ids.lib_box.add_widget(lib_player)
            #     queue = [app.songs[self.index]]
            #     player = PlayerScreen(name="player", queue=queue)
            #     app.root.add_widget(player)
            # else:
            #     player = app.root.get_screen("player")
            #     queue = [app.songs[self.index]]
            #     player.queue = queue


# TODO: move tracks in qv by holding button
class QueueView(RecycleView):
    hl_pos = NumericProperty()

    def update_qv(self):
        player = App.get_running_app().root.get_screen("player")
        self.data = [{"index": i,
                      "cover.source": player.metadts[i].image_path,
                      "title.text": player.metadts[i].tag.title,
                      "artist.text": player.metadts[i].tag.artist,
                      "duration.text": formated_time(player.metadts[i].tag.duration),
                      "now_playing": False}
                     for i in range(player.queue_length)]
        self.data[player.now_playing_pos]["now_playing"] = True
        self.hl_pos = player.now_playing_pos
        # Logger.info(self.data)

    def update_hl(self):
        player = App.get_running_app().root.get_screen("player")
        self.data[self.hl_pos]["now_playing"] = False
        self.data[player.now_playing_pos]["now_playing"] = True
        self.hl_pos = player.now_playing_pos
        self.refresh_from_data()


class QueueScreen(Screen):
    def update_queue_screen(self):
        self.ids.qv.update_qv()

    def update_hl(self):
        self.ids.qv.update_hl()


class CloseQueueButton(Button):
    def close_queue(self):
        # FIXME: screen turns a little white when transition works
        sm = App.get_running_app().root
        sm.transition = CardTransition()
        sm.transition.direction = "down"
        sm.transition.mode = "pop"
        sm.current = "player"


class PathView(RecycleKVIDsDataViewBehavior, BoxLayout):
    def remove_path(self):
        settings = App.get_running_app().root.get_screen("settings")
        psv = settings.ids.psv
        del psv.data[psv.paths_amount - 1]
        del settings.music_paths[psv.paths_amount - 1]
        psv.paths_amount -= 1
        with open(settings.file_path, "w") as f:
            json = dumps(settings.music_paths)
            f.write(json)


class PathsView(RecycleView):
    paths_amount = NumericProperty(0)


class SettingsButton(Button):
    def open_settings(self):
        sm = App.get_running_app().root
        sm.transition = NoTransition()
        sm.current = "settings"


class ScanIconButton(ButtonBehavior, Image):
    def scan(self):
        settings = App.get_running_app().root.get_screen("settings")
        if db_exists():
            remove_db()
        create_db(settings.music_paths)


class SettingsScreen(Screen):
    file_path = Path(get_cache_dir()).joinpath("music-paths.json")
    try:
        with open(file_path, "r") as f:
            json = f.read()
            json = loads(json)
    except FileNotFoundError:
        json = []
    music_paths = ListProperty(json)

    def update_settings_screen(self):
        self.ids.psv.paths_amount = 0
        self.ids.psv.data = []
        for i in range(len(self.music_paths)):
            self.ids.psv.paths_amount += 1
            self.ids.psv.data.append({"pos": self.ids.psv.paths_amount,
                                      "path_label.text": self.music_paths[i]})

    def save_music_path(self):
        settings = App.get_running_app().root.get_screen("settings")
        path = settings.ids.path_text_input.text
        if Path(path).is_dir():
            settings.ids.path_text_input.text = ""
            settings.ids.psv.paths_amount += 1
            settings.ids.psv.data.append({"pos": settings.ids.psv.paths_amount,
                                          "path_label.text": path})
            self.music_paths.append(path)
            with open(self.file_path, "w") as f:
                json = dumps(self.music_paths)
                f.write(json)
        else:
            Logger.error("Path is invalid")


class LibraryView(RecycleView):
    hl_pos = NumericProperty(0)
    row_ids = DictProperty()

    def update_lv(self):
        app = App.get_running_app()
        self.data = [{"index": i,
                      "cover.source": app.songs[i].image,
                      "title.text": app.songs[i].title,
                      "artist.text": app.songs[i].artist,
                      "duration.text": formated_time(app.songs[i].length),
                      "now_playing": False}
                     for i in range(len(app.songs))]
        self.row_ids = {song.id: i for i, song in enumerate(app.songs)}
        try:
            self.update_hl()
        except Exception:
            pass
        Logger.info(f"songs - {app.songs}")

    def update_hl(self):
        player = App.get_running_app().root.get_screen("player")
        self.data[self.hl_pos]["now_playing"] = False
        track_id = player.now_playing.id
        self.hl_pos = self.row_ids[track_id]
        self.data[self.hl_pos]["now_playing"] = True
        self.refresh_from_data()


class FilterButton(Button):
    pass


class LibraryFilter(GridLayout):
    pass


class LibraryPlayer(GridLayout, Button):
    track_pos = StringProperty("0:00/0:00")

    def open_player(self):
        sm = App.get_running_app().root
        sm.transition = SlideTransition()
        sm.transition.direction = "up"
        sm.current = "player"


class LibraryScreen(Screen):
    def update_lv(self):
        Clock.schedule_once(lambda dt: self.ids.lv.update_lv(), -1)

    def update_hl(self):
        self.ids.lv.update_hl()


class SimplePlayer(App):
    volume = BoundedNumericProperty(1, min=0, max=1,
                                    errorhander=lambda x: 1 if x > 1 else 0)
    volume_path = Path(get_cache_dir()).joinpath("volume.json")
    repeat = StringProperty("No repeat")
    repeat_variants = {"repeat": "Repeat",
                       "no_repeat": "No repeat",
                       "repeat_queue": "Repeat queue"}
    songs = ListProperty()
    lib_player = ObjectProperty(None)
    player = ObjectProperty(None)

    def update_songs(self, songs):
        self.songs = songs

    def build(self):
        self.font = Font.main
        Window.size = Size.minimal
        self.title = "Simple Player"

        sm = ScreenManager(transition=CardTransition())
        sm.add_widget(LibraryScreen(name="library"))
        sm.add_widget(SettingsScreen(name="settings"))
        # sm.add_widget(PlayerScreen(name="player"))
        # sm.add_widget(QueueScreen(name="queue"))
        return sm

    def on_repeat(self, obj, value):
        player = self.get_running_app().root.get_screen("player")
        if self.repeat_variants["repeat"] == self.repeat:
            player.sound_provider.loop = True
        if self.repeat_variants["no_repeat"] == self.repeat:
            player.sound_provider.loop = False
        if self.repeat_variants["repeat_queue"] == self.repeat:
            player.sound_provider.loop = False
            pass

    def update_lv(self):
        self.root.get_screen("library").ids.lv.update_lv()

    def on_start(self):
        try:
            with open(self.volume_path, "r") as f:
                json = f.read()
                json = loads(json)
                self.volume = json
        except FileNotFoundError:
            pass
        if db_exists():
            Clock.schedule_once(lambda dt: self.update_songs(get_all()), -1)
        Clock.schedule_once(lambda dt: self.update_lv(), -1)

    def on_stop(self):
        with open(self.volume_path, "w") as f:
            json = dumps(self.volume)
            f.write(json)


if __name__ == '__main__':
    SimplePlayer().run()
