import pytest
from src.config import DaemonConfig
from src.network import NetworkHandler

def test_config():
    config = DaemonConfig()
    assert config.host == "localhost"
    assert config.port == 9090
    assert config.command == "listen 1"

def test_network_handler():
    config = DaemonConfig()
    handler = NetworkHandler(config)
    # Note: Actual connection test would require a mock server
    assert handler.sock is None