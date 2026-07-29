"""
lmslogger key internals.  This connects to the LMS_HOST, issues the LMS_COMMAND,
and listens for output (based on the Lyrion Media Server debug flags, and others).  If
LMS_POLL_INTERVAL_SECONDS is reached, then a LMS_ALIVE_MESSAGES is issued.
"""
import argparse
import signal
import sys
import time
from .config import DaemonConfig
from .network import NetworkHandler

def signal_handler(signum: int, frame) -> None:  # type: ignore
    '''Handle shutdown signal from systemd gracefully'''
    print("Received signal, shutting down...", flush=True)
    sys.exit(0)

class Daemon:
    '''Main loop and connection management'''
    def __init__(self, config: DaemonConfig | None = None) -> None:
        self.config = config or DaemonConfig()
        self.handler = NetworkHandler(self.config)

    def connect_and_send_command(self) -> bool:
        '''Connect to LMS_HOST, and request messages'''
        if not self.handler.connect():
            return False
        self.handler.send_command(self.config.command)
        return True

    def run(self) -> None:
        '''Wait and listen for messages from LMS_HOST'''
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        if not self.connect_and_send_command():
            sys.exit(1)

        while True:
            data = self.handler.receive_data()
            if data is None:
                break

            if data == "":
                if self.config.alive_messages:
                    print("No data received; still alive.", flush=True)
                time.sleep(self.config.poll_interval_seconds)
                continue

        self.handler.close()


def parse_args() -> argparse.Namespace:
    '''Handle command-line arguments'''
    parser = argparse.ArgumentParser(
        prog="lmslogger",
        description="Run the LMS logger daemon with optional CLI configuration.",
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to a .env file containing LMS_ environment variables",
    )
    parser.add_argument("--host", help="LMS host to connect to")
    parser.add_argument("--port", type=int, help="LMS port to connect to")
    parser.add_argument("--command", help="Command to send to LMS after connecting")
    parser.add_argument("--poll-interval", type=int, help="Seconds to wait between heartbeat polls")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--alive-messages",
        dest="alive_messages",
        action="store_true",
        help="Print alive messages when no data is received",
    )
    group.add_argument(
        "--no-alive-messages",
        dest="alive_messages",
        action="store_false",
        help="Do not print alive messages when no data is received",
    )
    parser.set_defaults(alive_messages=None)
    return parser.parse_args()


def build_config(args: argparse.Namespace) -> DaemonConfig:
    '''Build configuration object'''
    config_kwargs: dict[str, object] = {}
    if args.host is not None:
        config_kwargs["host"] = args.host
    if args.port is not None:
        config_kwargs["port"] = args.port
    if args.command is not None:
        config_kwargs["command"] = args.command
    if args.poll_interval is not None:
        config_kwargs["poll_interval_seconds"] = args.poll_interval
    if args.alive_messages is not None:
        config_kwargs["alive_messages"] = args.alive_messages

    return DaemonConfig(_env_file=args.env_file, **config_kwargs)


def main() -> None:
    '''run daemon'''
    args = parse_args()
    daemon = Daemon(build_config(args))
    daemon.run()

if __name__ == "__main__":
    main()
