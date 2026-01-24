import json
from pathlib import Path

DATA_FILE = Path("data.json")

DEFAULT_DATA = {
    "channels": [],
    "check_interval": 6
}


def load_data() -> dict:
    if not DATA_FILE.exists():
        save_data(DEFAULT_DATA)

    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data: dict) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
