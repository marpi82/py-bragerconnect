"""
Python library to connect BragerConnect and Home Assistant to work together.

Platform classes
"""

from dataclasses import dataclass


@dataclass
class Sensor:
    """BragerConnect Sensor base model"""


@dataclass
class BinarySensor(Sensor):
    """BragerConnect BinarySensor base model"""
