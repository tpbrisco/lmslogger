"""
Configuration options for LMS logger - priority for fields is
- configuration file
- environment variable
- command line

Set host, port, command to send to lms server, frequency of polling, and
whether "keepalive" messages are issued
"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class DaemonConfig(BaseSettings):
    '''Configuration options for lmslogger'''
    host: str = Field(default="localhost")
    port: int = Field(default=9090)
    command: str = Field(default="listen 1")
    poll_interval_seconds: int = Field(default=60)
    alive_messages: bool = Field(default=True)

    model_config = SettingsConfigDict(env_prefix="LMS_", env_file=".env")
