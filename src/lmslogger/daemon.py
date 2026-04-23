import signal
import sys
import time
from .config import DaemonConfig
from .network import NetworkHandler

def signal_handler(signum: int, frame) -> None:  # type: ignore
    print("Received signal, shutting down...", flush=True)
    sys.exit(0)

class Daemon:
    def __init__(self) -> None:
        self.config = DaemonConfig()
        self.handler = NetworkHandler(self.config)

    def connect_and_send_command(self) -> bool:
        if not self.handler.connect():
            return False
        self.handler.send_command(self.config.command)
        return True

    def run(self) -> None:
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

def main() -> None:
    daemon = Daemon()
    daemon.run()

if __name__ == "__main__":
    main()
