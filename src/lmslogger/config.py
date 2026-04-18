from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class DaemonConfig(BaseSettings):
    host: str = Field(default="localhost")
    port: int = Field(default=9090)
    command: str = Field(default="listen 1")
    poll_interval_seconds: int = Field(default=60)
    alive_messages: bool = Field(default=True)

    model_config = SettingsConfigDict(env_prefix="LMS_", env_file=".env")