import os
from core.config import BaseConfig


class Config(BaseConfig):
    """Database Configuration"""

    def __init__(self):
        super().__init__()
        self.database_url = os.getenv("DATABASE_URL", "")
        self.connect_timeout = self.get_int("DATABASE_CONNECT_TIMEOUT", 20)
        self.database_echo = self.get_int("DATABASE_ECHO", 0)

config = Config()