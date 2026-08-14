##!/home/black-fox/smpl/venv/bin/python3
import kivy

kivy.require('2.3.1')

from threading import Thread

import kivy.uix.recycleview

from pynput import keyboard
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.logger import Logger
from kivy.graphics import Color, Rectangle
from kivy.properties import (BooleanProperty, BoundedNumericProperty,
                             ListProperty, NumericProperty, ObjectProperty,
                             StringProperty)
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.uix.spinner import Spinner
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import CardTransition, Screen, ScreenManager
from kivy.uix.recycleview.views import RecycleKVIDsDataViewBehavior
from kivy.core.audio import SoundLoader
from kivy.core.window import Window

from utils import application_path, tracks
from config import Color as Clr, Font, Size
from metadata import Metadata

__version__ = "1.0.0"

Config.set("input", "mouse", "mouse,multitouch_on_demand")

play_from = 0

# TODO: better logging
# TODO: use outer audio engine, not kivy's?

# TODO: move it to utils
def formated_time(time: int|float) -> str:
    mins = int((time / 60))
    secs = int(time - mins * 60)
    return f"{mins}:{secs:02}"

# TODO: if audio device is disconnected stop music

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
        if root.sound_provider.state == 'stop':
            save_pos = root.sound_provider.get_pos()
            # root.sound_provider.seek(save_pos)
            # Logger.info(f'SEEK1: {save_pos}')
            root.sound_provider.play()
            Logger.info('Player: Start playing')
            # Logger.info(root.sound_provider.get_pos())
            Clock.schedule_once(lambda dt: root.sound_provider.seek(save_pos), 0)
            Logger.info(f'Player: Seek {save_pos}')
            # Logger.info(root.sound_provider.get_pos())
            # root.start_time_events(self)
            # self.text = 'Stop'
            # self.background_on_start(self) else:
            # self.text = 'Play'
        else:
            root.sound_provider.stop()
            # root.stop_time_events()
            # self.background_on_pause(self)
            Logger.info('Stop playing')

    def background_on_play(self, obj):
        # Logger.info('playb')
        self.background_down = f'{application_path}/resources/images/play_circle.png'
        self.background_normal = f'{application_path}/resources/images/pause_circle.png'

    def background_on_pause(self, obj):
        # Logger.info('pauseb')
        self.background_down = f'{application_path}/resources/images/play_circle.png'
        self.background_normal = f'{application_path}/resources/images/play_circle.png'


class PreviousButton(Button):
    def play_previous(self):
        root = App.get_running_app().root.get_screen("player")
        # TODO: go back if this first track or time after start < config t
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
        sm.transition.direction = "up"
        sm.transition.mode = "push"
        sm.current = "queue"


class PlayerBackButton(Button):
    def go_back(self):
        Logger.info("TODO: go back from player")


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

    queue_length = NumericProperty(len(tracks))
    now_playing_pos = NumericProperty(play_from)
    queue = ListProperty(tracks)
    now_playing = StringProperty(tracks[play_from])
    sound_provider = ObjectProperty(SoundLoader.load(tracks[play_from]), rebind=True)
    metadt = ObjectProperty(Metadata(tracks[play_from]), rebind=True)
    metadts = ListProperty([Metadata(track) for track in tracks])
    slider_value = NumericProperty(0)
    track_pos = NumericProperty(0)
    length = NumericProperty(0)

    def __init__(self, **kwargs):
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
        Clock.schedule_once(lambda dt: self.bind_play_button(), -1)
        Clock.schedule_once(lambda dt: self.bind_update_pos(), -1)
        Clock.schedule_once(lambda dt:
                            self.sound_provider.bind(on_stop=self.auto_play_next), -1)
        Clock.schedule_once(lambda dt: self.set_length(), -1)

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

    def on_now_playing_pos(self, obj, value):
        self.now_playing = self.queue[self.now_playing_pos]
        prev_track_state = self.sound_provider.state
        prev_track_loop = self.sound_provider.loop
        if prev_track_state == "play":
            self.sound_provider.stop()
        self.sound_provider.unload()
        self.sound_provider = SoundLoader.load(self.now_playing)
        self.metadt = Metadata(self.now_playing)
        Logger.info(f"New sound {self.metadt.tag.title}")
        self.set_length()
        self.bind_play_button()
        self.bind_update_pos()
        self.sound_provider.bind(on_stop=self.auto_play_next)
        app = App.get_running_app()
        self.sound_provider.volume = app.volume
        self.sound_provider.loop = prev_track_loop
        if prev_track_state == "play":
            self.sound_provider.play()
        root = app.root
        screen = root.current
        if screen == "queue":
            root.get_screen(screen).update_hl()

    def bind_play_button(self):
        self.sound_provider.bind(on_play=self.ids.play_button.background_on_play)
        self.sound_provider.bind(on_stop=self.ids.play_button.background_on_pause)
        pass

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
        self.sound_provider.bind(on_play=self.start_time_events)
        self.sound_provider.bind(on_stop=self.stop_time_events)

    def stop_time_events(self, obj):
        Logger.info('stop_events')
        self.update_slider_value_event.cancel()
        self.update_pos_event.cancel()

    def start_time_events(self, obj):
        Logger.info('start_events')
        self.update_slider_value_event()
        self.update_pos_event()

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

    def play_track(self):
        player = App.get_running_app().root.get_screen("player")
        if not self.now_playing:
            player._set_now_playing_pos(self.index)


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
            sm.transition.direction = "down"
            sm.transition.mode = "pop"
            sm.current = "player"


class SimplePlayer(App):
    volume = BoundedNumericProperty(1, min=0, max=1,
                                    errorhander=lambda x: 1 if x > 1 else 0)
    repeat = StringProperty("No repeat")
    repeat_variants = {"repeat": "Repeat",
                       "no_repeat": "No repeat",
                       "repeat_queue": "Repeat queue"}

    def build(self):
        self.font = Font.main
        Window.size = Size.minimal
        self.title = "Simple Player"

        sm = ScreenManager(transition=CardTransition())
        sm.add_widget(PlayerScreen(name="player"))
        sm.add_widget(QueueScreen(name="queue"))
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

    def on_start(self):
        pass

    def on_stop(self):
        pass
        # Metadata.clear_cache()


if __name__ == '__main__':
    SimplePlayer().run()
