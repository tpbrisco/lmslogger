import signal
import sys
from .config import DaemonConfig
from .network import NetworkHandler

def signal_handler(signum, frame):
    print("Received signal, shutting down...")
    sys.exit(0)

def main():
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    config = DaemonConfig()
    handler = NetworkHandler(config)

    if not handler.connect():
        sys.exit(1)

    handler.send_command(config.command)

    while True:
        data = handler.receive_data()
        if data is None:
            break

    handler.close()

if __name__ == "__main__":
    main()