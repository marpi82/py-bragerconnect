"""
Python library to connect BragerConnect and Home Assistant to work together.

Asynchronous WebSocket client
"""
from __future__ import annotations

import json
import logging
from socket import gaierror as GetAddressInfoError
from collections import deque  # pylint: disable=unused-import
from threading import Lock
from asyncio import AbstractEventLoop, Queue, get_running_loop, wait_for
from typing import Any, Optional, Final, Literal, Union, Awaitable, Callable

import backoff  # pylint: disable=unused-import

from websockets.client import WebSocketClientProtocol, connect as ws_connect
from websockets.exceptions import ConnectionClosed, InvalidURI, InvalidHandshake

from .models.websocket import Message, MessageType, ConnectionInfo, ResponseType, JsonType
from .exceptions import MessageException, AuthError
from .const import LOGGER, HOST, TIMEOUT


class Connection:
    """Main class for handling connections with BragerConnect WebSocket."""

    def __init__(
        self,
        username: str,
        password: str,
        language: str = "en",
        loop: Optional[AbstractEventLoop] = None,
    ) -> None:
        """Main class for handling connections with BragerConnect.

        Args:
            loop (Optional[asyncio.AbstractEventLoop], optional): Event loop. Defaults to None.
        """
        self._host: str = HOST
        self._username: str = username
        self._password: str = password
        self._language: str = language

        self._loop = loop if loop is not None else get_running_loop()
        self._responses: ResponseType = {}
        self._messages_counter: int = -1
        self._messages_counter_thread_lock: Lock = Lock()

        self._client: Optional[WebSocketClientProtocol] = None
        # self._device: Optional[list[BragerDevice]] = None
        # self._device_message: Optional[dict[str, Queue]] = None

        self._active_device_id: Optional[str] = None
        self._reconnect: bool = False

    @property
    def connection_info(self) -> ConnectionInfo:
        """Returns connection info object."""
        raise NotImplementedError  # TODO: collect connection info data

    @property
    def connected(self) -> bool:
        """Return if we are connect to the WebSocket of a BragerConnect service.

        Returns:
            bool: True if we are connected, False otherwise.
        """
        return self._client and not self._client.closed

    @property
    def reconnect(self) -> bool:
        """TODO: docstring"""
        return self._reconnect

    @reconnect.setter
    def reconnect(self, value: bool) -> None:
        """TODO: docstring"""
        self._reconnect = bool(value)

    async def connect(self) -> None:
        """Connect to BragerConnect WebSocket server.
        Authenticate user and sets default language

        Raises:
            ConnectionError: Error occurred while communicating with the BragerConnect.
            AuthError: Error occurred on logging in (wrong username and/or password).
            RuntimeError: Error occured while setting language.
        """
        if self.connected:
            return

        LOGGER.info("Connecting to BragerConnect WebSocket server.")
        try:
            self._client = await ws_connect(uri=self._host)
        except (
            InvalidURI,
            InvalidHandshake,
            TimeoutError,
            GetAddressInfoError,
        ) as exception:
            LOGGER.exception("Error connecting to BragerConnect.")
            raise ConnectionError(
                "Error occurred while communicating with BragerConnect service"
                f" on WebSocket at {self._host}"
            ) from exception

        LOGGER.debug("Waiting for READY_SIGNAL.")
        message = await wait_for(self._client.recv(), TIMEOUT)
        LOGGER.debug("Message received.")
        wrkfnc: JsonType = json.loads(message)

        if isinstance(wrkfnc, dict) and wrkfnc.get("type") == MessageType.READY_SIGNAL:
            LOGGER.debug("Got READY_SIGNAL, sending back, connection ready.")
            await self._client.send(message)
        else:
            LOGGER.exception("Received message is not a READY_SIGNAL, exiting")
            raise RuntimeError(
                "Error occurred while communicating with BragerConnect service."
                "READY_SIGNAL was expected."
            )

        LOGGER.info("Creating task for received messages processing")
        self._loop.create_task(self._process_messages())

        await self._login(self._username, self._password)

        if self._language:
            if not await self.wrkfnc_set_user_variable("preffered_lang", self._language):
                raise RuntimeError("Error setting language on BragerConnect service.")

        if not self._active_device_id:
            await self.wrkfnc_get_active_device_id()

        # if not self._device:
        #    await self.update()

    async def _login(self, username: str, password: str) -> bool:
        """Authenticates user with given credentials

        Args:
            username (str): Username used to login
            password (str): Password used to login

        Returns:
            bool: True if logged in, otherwise False
        """

        LOGGER.debug("Logging in.")
        try:
            result = await self.wrkfnc_execute(
                "s_login",
                [
                    username,
                    password,
                    None,
                    None,
                    "bc_web",  # IDEA: could be a `bc_web` or `ht_app - what does it mean?
                ],
            )
        except MessageException as exception:
            raise AuthError("Error when logging in (wrong username/password)") from exception
        else:
            return result == 1

    async def _process_messages(self) -> None:
        """Main function that processes incoming messages from Websocket."""
        try:
            async for message in self._client:
                wrkfnc: JsonType = json.loads(message)
                if wrkfnc is not None and wrkfnc.get("wrkfnc"):
                    LOGGER.debug("Received response: %s", message)
                    message_id = wrkfnc.get("nr")
                    if message_id is not None:
                        # It is a response for request sent
                        if len(self._responses) > 0:
                            self._responses.pop(message_id).set_result(wrkfnc)
                    else:
                        # It is a request
                        await self._process_request(wrkfnc)
                else:
                    LOGGER.error("Received message type is not known, skipping.")
                    continue
        except ConnectionClosed:
            LOGGER.info("BragerConnect connection lost.")
            if self.reconnect:
                await self.connect()
            else:
                await self.close()

    async def _process_request(self, wrkfnc: dict) -> None:
        """Function that processes messages containing the actions to be performed (requests)

        Args:
            wrkfnc (dict): Dictionary containing message variables
        """
        LOGGER.debug(
            "Received request to execute: %s(args=%s)",
            wrkfnc["name"],
            wrkfnc["args"],
        )

    async def _send_wrkfnc(
        self,
        wrkfnc_name: str,
        wrkfnc_args: Optional[list] = None,
        wrkfnc_type: MessageType = MessageType.FUNCTION_EXEC,
    ) -> int:
        """Sends message. JSON formatted

        Args:
            wrkfnc_name (str): Function name to execute on server side
            wrkfnc_args (Optional[list], optional): Function parameters list. Defaults to None.
            wrkfnc_type (MessageType, optional): Message type. Defaults to FUNCTION_EXEC.

        Returns:
            int: Sent messade ID
        """
        message_id = self._generate_message_id()
        message = json.dumps(
            {
                "wrkfnc": True,
                "type": wrkfnc_type,
                "name": f"{wrkfnc_name}",
                "nr": message_id,
                "args": wrkfnc_args if wrkfnc_args is not None else [],
            }
        )

        LOGGER.debug("Sending function to execute: %s", message)
        await self._client.send(message)

        return message_id

    async def _wait_wrkfnc(self, message_id: int) -> JsonType:
        """Waiting to receive response for message `message_id`

        Args:
            message_id (int): Message ID number.

        Raises:
            BragerError: When timeout occurs.

        Returns:
            JsonType: (str) Received message
        """

        try:
            result: JsonType = await wait_for(
                self._responses.setdefault(message_id, self._loop.create_future()),
                TIMEOUT,
            )
        except TimeoutError as exception:
            LOGGER.exception("Timed out while processing request response.")
            raise RuntimeError(
                "Timed out while processing request response from BragerConnect service."
            ) from exception
        else:
            if result.get("type") == MessageType.EXCEPTION:
                LOGGER.exception("Exception response received.")
                raise MessageException("Exception occured while processing request response.")
            return result.get("resp")

    async def wrkfnc_execute(
        self,
        wrkfnc_name: str,
        wrkfnc_args: Optional[list[str]] = None,
        wrkfnc_type: MessageType = MessageType.FUNCTION_EXEC,
    ) -> JsonType:
        """Sends a request to perform request on server side and waits for the response.

        Args:
            wrkfnc_name (str): Function name to execute.
            wrkfnc_args (Optional[list], optional): Function parameters list. Defaults to None.
            wrkfnc_type (MessageType, optional): Message type. Defaults to FUNCTION_EXEC.

        Returns:
            JsonType: Server response
        """
        return await self._wait_wrkfnc(
            await self._send_wrkfnc(wrkfnc_name, wrkfnc_args, wrkfnc_type),
        )

    async def wrkfnc_get_device_id_list(self) -> list[JsonType]:
        """Gets a list of dictionaries with information about devices from the server.

        Returns:
            list[JsonType]: list of dictionaries with information about devices.
        """
        return await self.wrkfnc_execute("s_getMyDevIdList", []) or []

    async def wrkfnc_get_active_device_id(self) -> str:
        """Gets the ID of the active device on the server

        Returns:
            str: Active device ID
        """
        LOGGER.debug("Getting active device id.")
        _device_id = await self.wrkfnc_execute("s_getActiveDevid", [])
        device_id = str(_device_id)
        self._active_device_id = device_id
        return device_id

    async def wrkfnc_set_active_device_id(self, device_id: str) -> bool:
        """Sets the ID of the active device on the server

        Args:
            device_id (str): Device ID to set active

        Returns:
            bool: True if setting was successfull, otherwise False
        """
        LOGGER.debug("Setting active device id to: %s.", device_id)
        result = await self.wrkfnc_execute("s_setActiveDevid", [device_id]) is True
        self._active_device_id = device_id
        return result

    async def wrkfnc_get_user_variable(self, variable_name: str) -> str:
        """TODO: docstring"""
        return await self.wrkfnc_execute("s_getUserVariable", [variable_name])

    async def wrkfnc_set_user_variable(self, variable_name: str, value: str) -> bool:
        """TODO: docstring"""
        return await self.wrkfnc_execute("s_setUserVariable", [variable_name, value]) is None

    async def wrkfnc_get_all_pool_data(self) -> JsonType:
        """TODO: docstring"""
        LOGGER.debug("Getting pool data for %s.", self._active_device_id)
        return await self.wrkfnc_execute("s_getAllPoolData", [])

    async def wrkfnc_get_task_queue(self) -> JsonType:
        """TODO: docstring"""
        LOGGER.debug("Getting tasks data for %s.", self._active_device_id)
        return await self.wrkfnc_execute("s_getTaskQueue", [])

    async def wrkfnc_get_alarm_list(self) -> JsonType:
        """TODO: docstring"""
        LOGGER.debug("Getting alarms data for %s.", self._active_device_id)
        return await self.wrkfnc_execute("s_getAlarmListExtended", [])

    def _generate_message_id(self) -> int:
        """Generates the next message ID number to sent request

        Returns:
            int: Message ID number.
        """
        with self._messages_counter_thread_lock:
            self._messages_counter += 1
            return self._messages_counter

    async def close(self) -> None:
        """Close WebSocket connection."""
        if not self._client or not self.connected:
            return
        LOGGER.info("Disconnecting from BragerConnect service.")
        self._reconnect = False
        await self._client.close()

    async def __aenter__(self) -> Connection:
        """Async enter.
        Returns:
            The BragerConnect object.
        """
        return self

    async def __aexit__(self, *_exc_info: Any) -> None:
        """Async exit.
        Args:
            _exc_info: Exec type.
        """
        await self.close()


if __name__ == "__main__":
    import sys
    from asyncio import run  # pylint: disable=ungrouped-imports

    async def main(username, password):
        """Main coroutine"""
        async with Connection(username, password) as client:
            await client.connect()

    LOGGER.setLevel(logging.DEBUG)
    LOGGER.addHandler(logging.StreamHandler(sys.stdout))
    sys.exit(run(main(sys.argv[1], sys.argv[2])))
