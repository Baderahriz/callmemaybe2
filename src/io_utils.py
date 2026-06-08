import json
from pathlib import Path


def load_json(path: str):
    with open(path, "r") as file:
        return json.load(file)


def write_json(path: str, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w") as file:
        json.dump(data, file, indent=2)
