"""JSON Utils"""

import json
from typing import Any

import aiofiles


async def read_json_async(file_path: str) -> Any:  # pyright: ignore[reportExplicitAny]
    """Open and deserialize a JSON file to a Python object

    Args:
        file_path (`str`): Path to JSON file

    Returns:
        `list | dict`: Deserialized JSON as a Python object
    """
    async with aiofiles.open(file_path, mode="r", encoding="utf8") as jsonfile:
        raw_json = await jsonfile.read()
    deserialized_json = json.loads(raw_json)
    return deserialized_json


async def write_json_async(file_path: str, content: Any) -> None:  # pyright: ignore[reportExplicitAny]
    """Serialize a Python object to a JSON string and write to a file

    Args:
        file_path (`str`): Path to JSON file
        content (`list | dict]`): Python object to convert to JSON
    """
    async with aiofiles.open(file_path, mode="w", encoding="utf8") as jsonfile:
        await jsonfile.write(json.dumps(content, indent=4))
