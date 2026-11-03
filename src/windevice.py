from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger

from winrt.system import Object
from winrt.windows.media.devices import (AudioDeviceRole,
                                         DefaultAudioRenderDeviceChangedEventArgs,
                                         MediaDevice)
from winrt.windows.devices.enumeration import (DeviceClass, DeviceInformation,
                                               DeviceInformationUpdate,
                                               DeviceWatcher)


class WinDevice:
    def __init__(self):
        self.current_device = None
        self.watcher = None
        self.update_current_device()
        self.update_watcher()
        self.defalult_audio_event_token = None

    def on_default_audio_device_changed(self, object: Object,
                                        default_audio_render_device_changed_event_args: DefaultAudioRenderDeviceChangedEventArgs):
        if (self.current_device != default_audio_render_device_changed_event_args.id
                and default_audio_render_device_changed_event_args.role == AudioDeviceRole.DEFAULT):
            self.update_current_device()
            Logger.info(f"WinDevice: New device - {self.current_device}")
            app = App.get_running_app()
            if app is not None:
                player = app.player
                if player is not None:
                    # Using Clock more than once causes events not to fire
                    # Gstreamer doesn't change output device when playing
                    if player.sound_provider.state == "play":
                        player.pause()
                        Clock.schedule_once(lambda dt: player.toggle_play(), 0)

    def on_remove(self, watcher: DeviceWatcher, device_info: DeviceInformationUpdate):
        if device_info.id == self.current_device:
            app = App.get_running_app()
            if app is not None:
                player = app.player
                if player is not None:
                    Clock.schedule_once(lambda dt: player.pause(), 0)
                    Logger.info("WinDevice: Default device removed. Playback is paused")

    def update_current_device(self):
        self.current_device = MediaDevice.get_default_audio_render_id(AudioDeviceRole.DEFAULT)

    def update_watcher(self):
        self.watcher = DeviceInformation.create_watcher(DeviceClass.AUDIO_RENDER)
        self.watcher.add_removed(self.on_remove)
        self.watcher.start()


def start_win_device():
    app = App.get_running_app()
    app.device = WinDevice()
    app.device.defalult_audio_event_token = MediaDevice.add_default_audio_render_device_changed(app.device.on_default_audio_device_changed)
    Logger.info("WinDevice: Started")


def stop_win_device():
    app = App.get_running_app()
    MediaDevice.remove_default_audio_capture_device_changed(app.device.default_audio_event_token)


if __name__ == "__main__":
    import asyncio

    async def sleeper():
        await asyncio.sleep(20)

    device = WinDevice()
    print(device.current_device)
    MediaDevice.add_default_audio_render_device_changed(device.on_default_audio_device_changed)
    asyncio.run(sleeper())
