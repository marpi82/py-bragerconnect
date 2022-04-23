"""Python library to connect BragerConnect and Home Assistant to work together."""
import logging
from asyncio import sleep

from .const import LOGGER
from .websocket import Connection
from .gateway import Gateway

if __name__ == "__main__":
    import sys
    from asyncio import run  # pylint: disable=ungrouped-imports

    async def main(username, password):
        """Main coroutine"""
        async with Gateway(Connection(username, password)) as gateway:
            await gateway.async_update_devices()
            await sleep(1)
            await sleep(1)

            for device in gateway.device:
                print(device.info)

    LOGGER.setLevel(logging.DEBUG)
    LOGGER.addHandler(logging.StreamHandler(sys.stdout))
    sys.exit(run(main(sys.argv[1], sys.argv[2])))
