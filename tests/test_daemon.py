import pytest
from lmslogger.config import DaemonConfig
from lmslogger.network import NetworkHandler

def test_config():
    config = DaemonConfig()
    assert config.host == "localhost"
    assert config.port == 9090
    assert config.command == "listen 1"
    assert config.poll_interval_seconds == 60
    assert config.alive_messages is True

def test_network_handler():
    config = DaemonConfig()
    handler = NetworkHandler(config)
    # Note: Actual connection test would require a mock server
    assert handler.sock is None