import asyncio

from kivy.logger import Logger

from main import SimplePlayer
from utils import get_dbus_support

dbus_support = get_dbus_support()
if dbus_support:
    from dbus import start_dbus

async def run_main_app(root, tasks):
    await root.async_run("asyncio")
    Logger.info("App finished")
    tasks.cancel()


if __name__ == '__main__':
    def root_func():
        app = SimplePlayer()
        tasks = asyncio.ensure_future(start_dbus())
        return asyncio.gather(run_main_app(app, tasks), tasks)
    if dbus_support:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(root_func())
        loop.close()
    else:
        SimplePlayer().run()
