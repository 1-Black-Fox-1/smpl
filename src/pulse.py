import signal
import asyncio

from contextlib import suppress

import pulsectl
import pulsectl_asyncio

from kivy.app import App
from kivy.logger import Logger

# import pulsectl
# print('Event types:', pulsectl.PulseEventTypeEnum)
# print('Event facilities:', pulsectl.PulseEventFacilityEnum)
# print('Event masks:', pulsectl.PulseEventMaskEnum)


class Pulse:
    def __init__(self):
        self.current_device = []

    async def listen(self):
        async with pulsectl_asyncio.PulseAsync("smpl") as pulse:
            async for event in pulse.subscribe_events("sink"):
                if (event.t == pulsectl.PulseEventTypeEnum.remove
                    and event.index == self.current_device.index):
                    Logger.info(f"Pulse: Device disconnected {self.current_device.name}. "
                                + "Music will be paused")
                    player = App.get_running_app().player
                    if player is not None:
                        player.pause()
                elif event.t == pulsectl.PulseEventTypeEnum.change:
                    old_device = self.current_device
                    await self.update_current_device()
                    if self.current_device.index != old_device.index:
                        Logger.info(f"Pulse: New device {self.current_device.name}")

    async def update_current_device(self):
        async with pulsectl_asyncio.PulseAsync("smpl") as pulse:
            self.current_device = await pulse.sink_default_get()


async def start_pulse():
    pulse = Pulse()
    await pulse.update_current_device()
    listen_task = asyncio.create_task(pulse.listen())
    Logger.info("Pulse: Started")
    try:
        await listen_task
    except asyncio.CancelledError:
        Logger.info("Pulse: Stopped")

if __name__ == "__main__":
    asyncio.run(start_pulse())
