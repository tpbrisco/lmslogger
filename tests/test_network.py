import socket
import argparse

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


def test_network_connect_failure(monkeypatch, capsys):
    class MockSocketFail:
        def __init__(self, *a, **k):
            pass

        def connect(self, addr):
            raise Exception("simulated connect failure")

        def settimeout(self, t):
            pass

    monkeypatch.setattr("lmslogger.network.socket.socket", lambda *a, **k: MockSocketFail())

    handler = NetworkHandler(DaemonConfig())
    result = handler.connect()
    captured = capsys.readouterr()
    assert result is False
    assert "Connection failed:" in captured.out


def test_network_receive_generic_exception(capsys):
    handler = NetworkHandler(DaemonConfig())

    class FakeSockError:
        def recv(self, n):
            raise RuntimeError("recv broken")

    handler.sock = FakeSockError()
    assert handler.receive_data() is None
    captured = capsys.readouterr()
    assert "Receive error:" in captured.out


def test_network_send_no_socket_noop(capsys):
    handler = NetworkHandler(DaemonConfig())
    handler.sock = None
    handler.send_command("nothing")
    captured = capsys.readouterr()
    assert captured.out == ""


def test_network_close_calls_socket_close():
    handler = NetworkHandler(DaemonConfig())

    class FakeSockClose:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    fs = FakeSockClose()
    handler.sock = fs
    handler.close()
    assert fs.closed is True


def test_network_connect_success(monkeypatch):
    class FakeSock:
        def __init__(self, *a, **k):
            self.timeout = None

        def connect(self, addr):
            # simulate successful connect
            self.addr = addr

        def settimeout(self, t):
            self.timeout = t

    monkeypatch.setattr("lmslogger.network.socket.socket", lambda *a, **k: FakeSock())

    cfg = DaemonConfig()
    handler = NetworkHandler(cfg)
    assert handler.connect() is True
    assert handler.sock is not None


def test_send_command_prints(capsys):
    handler = NetworkHandler(DaemonConfig())

    class FakeSockSend:
        def __init__(self):
            self.data = b""

        def sendall(self, b: bytes):
            self.data = b

    fs = FakeSockSend()
    handler.sock = fs
    handler.send_command("printme")
    captured = capsys.readouterr()
    assert "Sent: printme" in captured.out


def test_receive_data_prints(capsys):
    handler = NetworkHandler(DaemonConfig())

    class FakeSock:
        def recv(self, n):
            return b"payload%21"

    handler.sock = FakeSock()
    out = handler.receive_data()
    assert out == "payload!"
    captured = capsys.readouterr()
    assert "Received: payload!" in captured.out


def test_receive_returns_none_when_no_socket():
    handler = NetworkHandler(DaemonConfig())
    handler.sock = None
    assert handler.receive_data() is None


def test_receive_returns_none_on_empty_bytes():
    handler = NetworkHandler(DaemonConfig())

    class FakeSockEmpty:
        def recv(self, n):
            return b""

    handler.sock = FakeSockEmpty()
    assert handler.receive_data() is None
