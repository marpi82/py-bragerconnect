"""
Python library to connect BragerConnect and Home Assistant to work together.

WebSocket classes and types
"""
from __future__ import annotations

from asyncio import Future
from dataclasses import dataclass, field
from datetime import datetime
from json import loads
from enum import Enum, IntEnum
from typing import Optional, Union, Any
from websockets.connection import State

from bragerconnect.exceptions import MessageException


JsonType = Optional[dict[str, Union[list, dict, str]]]


class MessageType(IntEnum):
    """Received message type enum"""

    PROCEDURE_EXEC = 1
    FUNCTION_EXEC = 2
    READY_SIGNAL = 10
    FUNCTION_RESP = 12
    EXCEPTION = 20
    PORT_MESSAGE = 21


class WorkerTaskType(Enum):
    """Worker types for tasks"""

    SUCCESS = "taskSuccessConfirmation"
    OVERWRITE = "taskOverwriteConfimation"
    LIST_CHANGED = "taskListChanged"


class WorkerModuleType(Enum):
    """Worker types for tasks"""

    LIST_CHANGED = "moduleListChanged"
    SHARED_TO_ME = "moduleSharedToMe"


class WorkerType(Enum):
    """Message worker type enum"""

    TASK_SUCCESS = WorkerTaskType.SUCCESS.value
    TASK_OVERWRITE = WorkerTaskType.OVERWRITE.value
    TASK_LIST_CHANGED = WorkerTaskType.LIST_CHANGED.value
    MODULE_LIST_CHANGED = WorkerModuleType.LIST_CHANGED.value
    MODULE_SHARED_TO_ME = WorkerModuleType.SHARED_TO_ME.value
    POOL_DATA_CHANGED = "poolDataChanged"
    NEW_ALARMS = "newAlarms"


@dataclass
class Message:
    """BragerConnect WebSocket message model"""

    # TODO: https://stackoverflow.com/questions/38464302/wrapping-a-python-class-around-json-which-is-better
    _raw: JsonType = field(repr=False)
    wrkfnc: bool
    mtype: MessageType

    @staticmethod
    def from_json(json: str) -> ResponseMessage or RequestMessage:
        """Creates Message object from received message"""
        try:
            msg = loads(json)
            if not (_wrkfnc := bool(msg.get("wrkfnc"))):
                raise Exception
            _type = MessageType(int(msg.get("type")))
            _name = msg.get("name")
            _nr = msg.get("nr")
            _number = int(_nr) if _nr is not None else _nr
            _args = msg.get("args", [])
            _resp = msg.get("resp")
        except Exception as exception:
            raise MessageException(
                f"Error occured while processing message. ({json})"
            ) from exception
        else:
            if _number is not None and _name is None:
                return ResponseMessage(msg, _wrkfnc, _type, _number, _resp)
            else:
                return RequestMessage(msg, _wrkfnc, _type, _name, _args)


@dataclass
class RequestMessage(Message):
    """BragerConnect WebSocket request message model"""

    name: str
    args: Optional[list[Any]]


@dataclass
class ResponseMessage(Message):
    """BragerConnect WebSocket response message model"""

    number: int
    response: Optional[JsonType]


ResponseType = dict[int, Future[ResponseMessage]]


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
