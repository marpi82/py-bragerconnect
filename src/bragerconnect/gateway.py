"""
Python library to connect BragerConnect and Home Assistant to work together.

BragerConnect gateway
"""
from __future__ import annotations
from typing import Any

from .websocket import Connection
from .models.device import Device, DeviceInfo
from .const import LOGGER


class Gateway:
    """Main class handling data from BragerConnect service."""

    def __init__(self, connection: Connection) -> None:
        """Main class handling data from BragerConnect service."""
        self.conn = connection
        self.device: set[Device] = set()

    async def async_update(self):
        """TODO: docstring"""
        dev_list = await self.conn.async_get_device_id_list()
        dev_id = (str(dev) for dev in self.device)

        for device in self.device:
            if device.info.devid not in dev_list:
                

        for info in dev_list:
            if info not in (dev_id):
                LOGGER.debug("create")
                self.device.add(Device(self.conn, DeviceInfo.from_dict(info)))

    async def __aenter__(self) -> Gateway:
        """Async enter.
        Returns:
            The Gateway object.
        """
        await self.conn.connect()
        return self

    async def __aexit__(self, *_exc_info: Any) -> None:
        """Async exit.
        Args:
            _exc_info: Exec type.
        """
        await self.conn.close()
