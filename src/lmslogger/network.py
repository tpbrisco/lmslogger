import socket
import urllib.parse
from typing import Optional
from .config import DaemonConfig

class NetworkHandler:
    def __init__(self, config: DaemonConfig):
        self.config = config
        self.sock: Optional[socket.socket] = None

    def connect(self) -> bool:
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.config.host, self.config.port))
            self.sock.settimeout(10.0)
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def send_command(self, command: str) -> None:
        if self.sock:
            self.sock.sendall((command + "\n").encode())
            print(f"Sent: {command}")

    def receive_data(self) -> Optional[str]:
        if not self.sock:
            return None
        try:
            data = self.sock.recv(1024)
            if data:
                decoded = urllib.parse.unquote(data.decode())
                print(f"Received: {decoded}")
                return decoded
            else:
                return None
        except socket.timeout:
            return ""
        except Exception as e:
            print(f"Receive error: {e}")
            return None

    def close(self) -> None:
        if self.sock:
            self.sock.close()