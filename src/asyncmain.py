import asyncio
from enum import Enum
from kivy.logger import Logger

from main import SimplePlayer
from utils import get_dbus_support
from utils import get_win_media_support

dbus_support = get_dbus_support()
if dbus_support:
    from dbus import start_dbus


win_media_support = get_win_media_support()
if win_media_support:
    from winmedia import start_win_media


async def run_main_app(root, tasks):
    await root.async_run("asyncio")
    Logger.info("App finished")
    tasks.cancel()


class MediaSupport(Enum):
    DISABLED = 0
    DBUS = 1
    WINMEDIA = 2


def root_func(media_support: MediaSupport):
    app = SimplePlayer()
    if media_support == MediaSupport.DBUS:
        tasks = asyncio.ensure_future(start_dbus())
        return asyncio.gather(run_main_app(app, tasks), tasks)
    elif media_support == MediaSupport.WINMEDIA:
        tasks = asyncio.ensure_future(start_win_media())
        return asyncio.gather(run_main_app(app, tasks), tasks)
    assert("Unreachable")


if __name__ == '__main__':
    if dbus_support:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(root_func(MediaSupport.DBUS))
        loop.close()
    elif win_media_support:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(root_func(MediaSupport.WINMEDIA))
        loop.close()
    else:
        SimplePlayer().run()
