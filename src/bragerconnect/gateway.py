"""
Python library to connect BragerConnect and Home Assistant to work together.

BragerConnect gateway
"""
from __future__ import annotations

from .websocket import Connection
from .const import LOGGER


class Gateway:
    """Main class handling data from BragerConnect service."""

    def __init__(self, connection: Connection) -> None:
        """Main class handling data from BragerConnect service."""
        self._conn = connection

        self.sensors = {}

    async def update(self):
        """TODO: docstring"""
