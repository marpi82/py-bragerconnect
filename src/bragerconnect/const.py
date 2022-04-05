"""
Python library to connect BragerConnect and Home Assistant to work together.

Module constants
"""
import logging
from typing import Optional, Union


# Connection
HOST = "wss://cloud.bragerconnect.com"
TIMEOUT = 10


# Logger
LOGGER = logging.getLogger(__package__)
