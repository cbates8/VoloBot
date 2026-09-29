"""Critical Hit/Miss Utils"""

import aiofiles
from aiocsv import AsyncDictReader
from typing import Literal

from constants.paths import CRIT_TABLE_PATH, FUMBLE_TABLE_PATH


def validate_crit_percentage(input_percentage: int) -> bool:
    """Validate user input crit percentage.
    Percentage should be an integer between 1 and 100 (inclusive)

    Args:
        input_percentage (`int`): User input percentage representing critical hit severity

    Returns:
        `bool`: True if input is valid, False otherwise.
    """
    return input_percentage in range(1, 101)


def validate_damage_type(valid_types: list[str], input_type: str) -> str | Literal[False]:
    """Validate user input damage type

    Args:
        valid_types (`list[str]`): List of valid damage types
        input_type (`str`): User input damage type

    Returns:
        `str | Literal[False]`: damage type if it is valid, False otherwise.
    """
    input_type = input_type.lower()

    for full_dmg_type in valid_types:
        # Includes abreviation support for damge types (spelling bludgeoning is hard!)
        if input_type in (full_dmg_type, full_dmg_type[:2]):
            return full_dmg_type
    return False


async def read_crit_csv_async(path: str) -> tuple[list[str], dict[int, dict[str, str]]]:
    """Read from CSV representing a critical hit/miss table

    Result will look like the following:
    {
        1: {"slashing": "slashing description", "bludgeoning": "bludgeoning description", ...},
        2: {"slashing": "slashing description", "bludgeoning": "bludgeoning description", ...},
        ...
    }

    Args:
        path (`str`): Path to the CSV

    Returns:
        `tuple[list[str], dict[int, dict]]`: List of CSV headers, CSV data as dict of dicts
    """
    async with aiofiles.open(path, mode="r", encoding="utf8") as csvfile:
        csvreader = AsyncDictReader(csvfile)
        fieldnames = await csvreader.get_fieldnames()
        # Identify header for the "Roll" column
        # Roll integers (1-100) will become keys of the resulting dict
        roll_column = fieldnames[0]
        # Separate remaining column headers
        headers = fieldnames[1:]
        # Create dictionary from CSV data
        # Each item will consist of the roll as the key and dict representation of remaining columns as the value
        data = {int(row.pop(roll_column)): row async for row in csvreader}
    return headers, data


async def get_crit_result(crit_percentage: int, dmg_type: str) -> str:
    """Get critical hit result

    Args:
        crit_percentage (`int`): Percentage representing critical hit severity
        dmg_type (`str`): Type of damage being inflicted

    Returns:
        `str`: Description of the crit result
    """
    # Check for valid %
    if not validate_crit_percentage(crit_percentage):
        return "**Error:** Invalid Percentage Roll\nMust be value from 1-100"

    # Read crit table
    valid_dmg_types, crit_table = await read_crit_csv_async(CRIT_TABLE_PATH)

    # Check for valid type
    if not (clean_dmg_type := validate_damage_type(valid_dmg_types, dmg_type)):
        # using chr(10) as newline, because f-string doesn't support \n in expression part
        return f"**Error:** Invalid Damage Type\nSupported types: ```\n{chr(10).join(valid_dmg_types)}```"

    # % and type are valid, so return crit result
    return crit_table[crit_percentage][clean_dmg_type]


async def get_fumble_result(fumble_percentage: int) -> str:
    """Get critical miss result

    Args:
        fumble_percentage (`int`): Percentage representing critical miss severity

    Returns:
        `str`: Description of the fumble result
    """
    # Check for valid %
    if not validate_crit_percentage(fumble_percentage):
        return "**Error:** Invalid Percentage Roll\nMust be value from 1-100"

    # Read fumble table
    headers, fumble_table = await read_crit_csv_async(FUMBLE_TABLE_PATH)

    # % is valid, so return fumble result
    fumble_column = headers[0]
    return fumble_table[fumble_percentage][fumble_column]
