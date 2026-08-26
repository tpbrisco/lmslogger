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
