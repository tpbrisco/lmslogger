import socket
import urllib.parse
from typing import Optional
from .config import DaemonConfig

class NetworkHandler:
    '''General network I/O handling of connection to LMS_HOST'''
    def __init__(self, config: DaemonConfig):
        self.config = config
        self.sock: Optional[socket.socket] = None

    def connect(self) -> bool:
        '''Connect to LMS_HOST (on port LMSPORT), set up for receiving messages'''
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.config.host, self.config.port))
            self.sock.settimeout(10.0)
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def send_command(self, command: str) -> None:
        '''Send data to LMS_HOST'''
        if self.sock:
            self.sock.sendall((command + "\n").encode())
            print(f"Sent: {command}")

    def receive_data(self) -> Optional[str]:
        '''Read input from LMS_HOST'''
        if not self.sock:
            return None
        try:
            data = self.sock.recv(1024)
            if data:
                decoded = urllib.parse.unquote(data.decode())
                print(f"Received: {decoded}", flush=True)
                return decoded
            return None
        except socket.timeout:
            return ""
        except Exception as e:
            print(f"Receive error: {e}")
            return None

    def close(self) -> None:
        '''close network connection gracefully'''
        if self.sock:
            self.sock.close()
