from pathlib import Path


LOG_PATH = Path() / "log"
DATA_PATH = Path() / "data"


LOG_PATH.mkdir(parents=True, exist_ok=True)
DATA_PATH.mkdir(parents=True, exist_ok=True)