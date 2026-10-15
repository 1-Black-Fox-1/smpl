import asyncio

from kivy.logger import Logger

from dbus import start_dbus
from main import SimplePlayer


async def run_main_app(root, tasks):
    await root.async_run("asyncio")
    Logger.info("App finished")
    tasks.cancel()


if __name__ == '__main__':
    def root_func():
        app = SimplePlayer()
        tasks = asyncio.ensure_future(start_dbus())
        return asyncio.gather(run_main_app(app, tasks), tasks)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(root_func())
    loop.close()
