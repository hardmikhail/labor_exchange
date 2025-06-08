import os
from enum import IntEnum
from pathlib import Path

env_file_name = ".env." + os.environ.get("STAGE", "dev")
env_file_path = Path(__file__).parent.parent.resolve() / env_file_name


class TestIds(IntEnum):
    USER = 666
    COMPANY = 777
    JOB = 888
    RESPONSE = 999
