from pydantic import BaseModel
from typing import Optional

class DaemonConfig(BaseModel):
    host: str = "localhost"
    port: int = 9090
    command: str = "listen 1"