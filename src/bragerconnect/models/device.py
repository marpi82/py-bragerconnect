"""
Python library to connect BragerConnect and Home Assistant to work together.

Device classes
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional

from ..models.websocket import JsonType
from ..websocket import Connection


@dataclass
class DeviceInfo:
    """Object holding Brager Device information."""

    username: str  # "marpi82"
    sharedfrom_name: Optional[str]  # None
    devid: str  # "FTTCTBSLCE"
    distr_group: Optional[str] = None  # "ht"
    id_perm_group: Optional[int] = None  # 1
    permissions_enabled: Optional[bool] = None  # 1
    permissions_time_start: Optional[str] = None  # ":null, # TODO: datetime?
    permissions_time_end: Optional[str] = None  # ":null, # TODO: datetime?
    accepted: Optional[bool] = None  # ":1,
    verified: Optional[bool] = None  # ":1,
    name: Optional[str] = None  # ":"",
    description: Optional[str] = None  # ":"",
    producer_permissions: Optional[int] = None  # ":2,
    producer_code: Optional[int] = None  # ":"67",
    warranty_void: Optional[bool] = None  # ":null,
    last_activity_time: Optional[int] = None  # ":2,  # TODO: int?
    alert: Optional[bool] = None  # ":false

    @staticmethod
    def from_dict(data: list[JsonType]) -> DeviceInfo:
        """Returns DeviceInfo object
        Args:
            data: The data from the BragerConnect service API.
        Returns:
            A DeviceInfo object.
        """

        username = data.get("username")
        devid = data.get("devid")
        if username is None or devid is None:
            raise RuntimeError("BragerDeviceInfo data is incomplete, cannot construct info object.")

        name = data.get("name")
        if name == "":
            name = None

        description = data.get("description")
        if description == "":
            description = None

        warranty_void = data.get("warranty_void")
        if warranty_void is not None:
            warranty_void = bool(warranty_void)

        return DeviceInfo(
            username=username,
            sharedfrom_name=data.get("sharedfrom_name"),
            devid=devid,
            distr_group=data.get("distr_group"),
            id_perm_group=data.get("id_perm_group"),
            permissions_enabled=bool(data.get("permissions_enabled")),
            permissions_time_start=data.get("permissions_time_start"),
            permissions_time_end=data.get("permissions_time_end"),
            accepted=data.get("accepted"),
            verified=data.get("verified"),
            name=name,
            description=description,
            producer_permissions=data.get("producer_permissions"),
            producer_code=int(data.get("producer_code")),
            warranty_void=warranty_void,
            last_activity_time=data.get("last_activity_time"),
            alert=data.get("alert"),
        )


class Device:
    """Brager Device model"""

    conn: Connection
    info: DeviceInfo

    def __init__(self, connection: Connection, info: DeviceInfo) -> None:
        self.conn = connection
        self.info = info

    def __str__(self) -> str:
        return self.info.devid
