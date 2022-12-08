"""
Python library to connect BragerConnect and Home Assistant to work together.

Device classes
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, InitVar
from pathlib import Path
from typing import Any, Optional, Union

from ..models.websocket import JsonType
from ..websocket import Connection

PoolType = dict[int, dict[int, dict[str, Union[int, float, str]]]]


def reformat_pool_dict(pool_data: dict[str, JsonType]) -> PoolType:
    """Reformat Pool data

    Args:
        pool_data (dict[str, JsonType]): input type

    Returns:
        PoolType: output type
    """
    data = {}
    for pool_name, pool_value in pool_data.items():
        for field_name, field_value in pool_value.items():
            pool_no = int(pool_name[1:])
            field_no = int(field_name[1:])
            field_t = str(field_name[0])
            data.setdefault(pool_no, {}).setdefault(field_no, {})[field_t] = field_value

    return data


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


@dataclass
class Pool:
    """Brager Pool model"""

    data: PoolType = field(init=False, default_factory=dict)
    unit: dict[int, Any] = field(init=False, default_factory=dict)
    name: dict[str, dict[int, str]] = field(init=False, default_factory=dict)
    init_data: InitVar[dict] = None
    init_lang: InitVar[str] = "pl"

    def __post_init__(self, init_data, init_lang):
        """TODO: docstring"""
        if not init_data:
            raise RuntimeError("Pool data is empty, can't create Pool object")

        for pool_name, pool_value in init_data.items():
            for field_name, field_value in pool_value.items():
                pool_no = int(pool_name[1:])
                field_no = int(field_name[1:])
                field_t = str(field_name[0])
                self.data.setdefault(pool_no, {}).setdefault(field_no, {})[field_t] = field_value

        try:
            path = Path(__file__).parent.parent
            unit_f = open(f"{path}/lang/{init_lang}_unit.json", "r", encoding="utf-8")
            name_f = open(f"{path}/lang/{init_lang}_pool.json", "r", encoding="utf-8")
        except OSError as exception:
            raise RuntimeError("Could not open/read JSON file.") from exception
        else:
            # TODO: klucze jako int
            self.unit = json.load(unit_f)
            self.name = json.load(name_f)
        finally:
            unit_f.close()
            name_f.close()


class Device:
    """Brager Device model"""

    conn: Connection
    info: DeviceInfo
    pool: Pool

    def __init__(self, connection: Connection, info: DeviceInfo) -> None:
        self.conn = connection
        self.info = info

    async def create(self) -> Device:
        """TODO: docstring"""
        await self.conn.async_set_active_device_id(self.info.devid)
        pool = await self.conn.async_get_all_pool_data()
        self.pool = Pool(init_data=pool)
        return self

    def __str__(self) -> str:
        return self.info.devid
