from sys import platform
from enum import Enum
from asyncio import ensure_future, gather, get_event_loop

from kivy.logger import Logger

from main import SimplePlayer
from utils import get_dbus_support, get_win_media_support

dbus_support = get_dbus_support()
if dbus_support:
    from dbus import start_dbus

if platform == "linux":
    from pulse import start_pulse

    pulse_support = True

win_media_support = get_win_media_support()
if win_media_support:
    from winmedia import start_win_media

async def run_main_app(root, *args):
    await root.async_run("asyncio")
    Logger.info("App: App finished")
    tasks = args[0]
    for task in tasks:
        task.cancel()


class MediaSupport(Enum):
    DISABLED = 0
    DBUS = 1
    WINMEDIA = 2


def root_func(media_support: MediaSupport):
    app = SimplePlayer()
    if media_support == MediaSupport.DBUS and pulse_support:
        tasks = []
        task = ensure_future(start_dbus())
        tasks.append(task)
        task = ensure_future(start_pulse())
        tasks.append(task)
        return gather(run_main_app(app, tasks), *tasks)
    elif pulse_support:
        tasks = ensure_future(start_pulse())
        return gather(run_main_app(app, tasks), tasks)
    elif media_support == MediaSupport.WINMEDIA:
        tasks = ensure_future(start_win_media())
        return gather(run_main_app(app, tasks), tasks)
    assert ("Unreachable")


if __name__ == '__main__':
    if dbus_support:
        loop = get_event_loop()
        loop.run_until_complete(root_func(MediaSupport.DBUS))
        loop.close()
    elif win_media_support:
        loop = get_event_loop()
        loop.run_until_complete(root_func(MediaSupport.WINMEDIA))
        loop.close()
    else:
        SimplePlayer().run()
