"""
    This is a GUI for controlling and monitoring a Blueksy instance through HTTP Server and Kafka.
"""
from .server.model import ServerModel
from .components import SophysForm, SophysLogin, \
    SophysLed, QueueController, SophysApplication