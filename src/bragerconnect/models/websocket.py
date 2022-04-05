"""
Python library to connect BragerConnect and Home Assistant to work together.

WebSocket classes and types
"""
from __future__ import annotations

from asyncio import Future
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum

from websockets.connection import State


JsonType = Optional[dict[str, Union[list, dict, str]]]

ResponseType = dict[int, Future[JsonType]]


class MessageType(IntEnum):
    """Received message type enum"""

    PROCEDURE_EXEC = 1
    FUNCTION_EXEC = 2
    READY_SIGNAL = 10
    FUNCTION_RESP = 12
    EXCEPTION = 20
    PORT_MESSAGE = 21


@dataclass
class ConnectionInfo:
    """Connection information wrapper class"""

    host: str
    port: str
    session_start: datetime
    last_successfull: datetime
    last_failed: datetime
    last_failed_reason: None
    time_online: datetime
    connection_status: State
    messages_sent: int
    messages_received: int
    messages_dropped: int
    bytes_sent: int
    bytes_received: int
    reconnect_count: int
