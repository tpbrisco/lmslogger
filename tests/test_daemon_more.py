import sys
import signal
from types import SimpleNamespace

import pytest

from lmslogger.daemon import signal_handler, parse_args, build_config, Daemon
from lmslogger.config import DaemonConfig


def test_signal_handler_exits():
    with pytest.raises(SystemExit) as exc:
        signal_handler(signal.SIGTERM, None)
    assert exc.value.code == 0


def test_parse_args_alive_flags(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["lmslogger", "--alive-messages"])
    args = parse_args()
    assert args.alive_messages is True

    monkeypatch.setattr(sys, "argv", ["lmslogger", "--no-alive-messages"])
    args = parse_args()
    assert args.alive_messages is False


def test_build_config_reads_env_file(tmp_path):
    env_file = tmp_path / ".env_test"
    env_file.write_text("LMS_HOST=fromenv.example.com\nLMS_PORT=4242")

    args = SimpleNamespace(
        env_file=str(env_file),
        host=None,
        port=None,
        command=None,
        poll_interval=None,
        alive_messages=None,
    )

    cfg = build_config(args)
    assert cfg.host == "fromenv.example.com"
    assert cfg.port == 4242


def test_daemon_run_exits_on_connect_failure(monkeypatch):
    class MockHandlerFail:
        def __init__(self, config):
            self.config = config

        def connect(self):
            return False

        def send_command(self, command: str):
            pass

        def receive_data(self):
            return None

        def close(self):
            pass

    monkeypatch.setattr("lmslogger.daemon.NetworkHandler", MockHandlerFail)
    monkeypatch.setattr("signal.signal", lambda *a, **k: None)

    cfg = DaemonConfig()
    d = Daemon(cfg)
    with pytest.raises(SystemExit) as exc:
        d.run()
    assert exc.value.code == 1


def test_main_invokes_daemon(monkeypatch):
    class DummyDaemon:
        def __init__(self, cfg):
            self.cfg = cfg

        def run(self):
            # indicate run called
            print("daemon-run-called")

    monkeypatch.setattr("lmslogger.daemon.Daemon", DummyDaemon)
    monkeypatch.setattr("lmslogger.daemon.parse_args", lambda: SimpleNamespace(env_file=".env", host=None, port=None, command=None, poll_interval=None, alive_messages=None))

    # calling main should construct DummyDaemon and call run()
    from lmslogger.daemon import main

    main()


def test_run_module_as_main(monkeypatch):
    class DummyDaemon:
        def __init__(self, cfg):
            self.cfg = cfg

        def run(self):
            print("daemon-run-called")

    monkeypatch.setattr("lmslogger.daemon.Daemon", DummyDaemon)
    monkeypatch.setattr("lmslogger.daemon.parse_args", lambda: SimpleNamespace(env_file=".env", host=None, port=None, command=None, poll_interval=None, alive_messages=None))

    import runpy
    # Ensure argparse sees no unexpected CLI args
    monkeypatch.setattr(sys, "argv", ["lmslogger"])
    # Patch signal handlers and socket to avoid real network/system interactions
    monkeypatch.setattr("signal.signal", lambda *a, **k: None)
    import socket as _socket

    class FakeSock:
        def __init__(self, *a, **k):
            pass

        def connect(self, addr):
            return None

        def settimeout(self, t):
            pass

        def recv(self, n):
            return b""

        def close(self):
            pass
        def sendall(self, b: bytes):
            # no-op for tests
            return None

    monkeypatch.setattr(_socket, "socket", lambda *a, **k: FakeSock())
    monkeypatch.setattr("time.sleep", lambda *_: None)

    runpy.run_module("lmslogger.daemon", run_name="__main__")
