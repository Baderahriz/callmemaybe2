import json
from pathlib import Path
from typing import Any
import sys


def load_json(path: str) -> Any:
    """Load JSON data from a file.

    Args:
        path: Path to the JSON file to load.

    Returns:
        The parsed JSON content on success.

    Notes:
        Prints an error and exits on invalid JSON or missing file.
    """
    try:
        with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: input file not found: {path}")
        sys.exit(1)
    except json.JSONDecodeError as ex:
        print(f"Error: invalid JSON in {path}: {ex}")
        sys.exit(1)


def write_json(path: str, data: Any) -> None:
    """Write data to a JSON file, creating parent directories.

    Args:
        path: Destination path for the JSON file.
        data: Data to serialize to JSON.

    Returns:
        None
    """
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w") as file:
        json.dump(data, file, indent=2)
