"""
Python library to connect BragerConnect and Home Assistant to work together.

BragerConnect gateway
"""
from __future__ import annotations
from typing import Any

from bragerconnect.models.websocket import JsonType

from .websocket import Connection
from .models.device import Device, DeviceInfo
from .const import LOGGER

from pydantic import ValidationError


class Gateway:
    """Main class handling data from BragerConnect service."""

    def __init__(self, connection: Connection) -> None:
        """Main class handling data from BragerConnect service."""
        self.conn = connection
        self.device: list[Device] = []

    async def async_update_devices(self):
        """Updates all devices from BragerConnect service."""
        actual_dev_list = await self.conn.async_get_device_id_list()
        actual_dev_id = {dev.get("devid") for dev in actual_dev_list}
        created_dev_id = {str(dev) for dev in self.device}

        # Remove not existing devices from self.device
        remove_list = (dev for dev in created_dev_id.difference(actual_dev_id))
        for device in reversed(self.device):
            if str(device) in remove_list:
                self.device.remove(device)

        # Create or update devices
        for info in actual_dev_list:
            devid = info.get("devid")
            if devid in created_dev_id:
                for device in self.device:
                    if device.info.devid == devid:
                        LOGGER.debug("Updating: %s", devid)
                        # device.info = DeviceInfo.from_dict(info)
            else:
                LOGGER.debug("Creating device: %s", devid)
                self.device.append(await Device(self.conn, DeviceInfo(**info)).create())

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
