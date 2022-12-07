"""
Python library to connect BragerConnect and Home Assistant to work together.

Module constants
"""
import logging
from typing import Optional, Union


# Connection
HOST = "wss://cloud.bragerconnect.com"
# HOST = "wss://sigma-dev.brager.dev"
TIMEOUT = 10


# Logger
LOGGER = logging.getLogger(__package__)
