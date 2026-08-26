import socket
import argparse

import pytest

from lmslogger.config import DaemonConfig
from lmslogger.network import NetworkHandler
from lmslogger.daemon import Daemon, build_config


def test_build_config_from_namespace():
    args = argparse.Namespace(
        env_file=".env",
        host="example.com",
        port=1234,
        command="status",
        poll_interval=5,
        alive_messages=False,
    )
    cfg = build_config(args)
    assert isinstance(cfg, DaemonConfig)
    assert cfg.host == "example.com"
    assert cfg.port == 1234
    assert cfg.command == "status"
    assert cfg.poll_interval_seconds == 5
    assert cfg.alive_messages is False


def test_daemon_connect_and_send_command_calls_send(monkeypatch):
    sent = {}

    class MockHandler:
        def __init__(self, config):
            self.config = config

        def connect(self):
            return True

        def send_command(self, command: str):
            sent["cmd"] = command

    monkeypatch.setattr("lmslogger.daemon.NetworkHandler", MockHandler)

    cfg = DaemonConfig()
    d = Daemon(cfg)
    assert d.connect_and_send_command() is True
    assert sent.get("cmd") == cfg.command


def test_daemon_run_prints_alive_and_exits(monkeypatch, capsys):
    # Handler that returns an empty string once (timeout) and then None (stop)
    class SeqHandler:
        def __init__(self, config):
            self.config = config
            self.calls = 0

        def connect(self):
            return True

        def send_command(self, command: str):
            pass

        def receive_data(self):
            self.calls += 1
            if self.calls == 1:
                return ""
            return None

        def close(self):
            pass

    monkeypatch.setattr("lmslogger.daemon.NetworkHandler", SeqHandler)
    monkeypatch.setattr("signal.signal", lambda *a, **k: None)
    monkeypatch.setattr("time.sleep", lambda *_: None)

    cfg = DaemonConfig()
    cfg.poll_interval_seconds = 0
    cfg.alive_messages = True
    d = Daemon(cfg)
    d.run()

    captured = capsys.readouterr()
    assert "No data received; still alive." in captured.out


def test_network_receive_decoded_data():
    handler = NetworkHandler(DaemonConfig())

    class FakeSock:
        def recv(self, n):
            return b"hello%20world"

    handler.sock = FakeSock()
    assert handler.receive_data() == "hello world"


def test_network_receive_timeout():
    handler = NetworkHandler(DaemonConfig())

    class FakeSockTimeout:
        def recv(self, n):
            raise socket.timeout

    handler.sock = FakeSockTimeout()
    assert handler.receive_data() == ""


def test_network_send_command_sends_bytes():
    handler = NetworkHandler(DaemonConfig())

    class FakeSockSend:
        def __init__(self):
            self.data = b""

        def sendall(self, b: bytes):
            self.data = b

    fs = FakeSockSend()
    handler.sock = fs
    handler.send_command("mycmd")
    assert fs.data == b"mycmd\n"
