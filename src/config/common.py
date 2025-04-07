import os
from pathlib import Path

env_file_name = ".env." + os.environ.get("STAGE", "dev")
env_file_path = Path(__file__).parent.parent.resolve() / env_file_name
