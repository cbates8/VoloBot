"""Combat Utils"""

import os
from dataclasses import asdict

from discord import Embed

from constants.paths import LIVE_COMBAT_PATH, SAVED_COMBAT_DIR
from utils.combat.types import RAW_CHAR_DICT_TYPE
from utils.combat.character import (
    CombatData,
    load_character_from_args,
    load_character_from_file,
    update_character_from_args,
    update_pc,
)
from utils.combat.formatting import get_combat_embed
from utils.json_utils import read_json_async, write_json_async
from utils.logging import get_logger

LOGGER = get_logger(os.path.basename(__file__))


def get_combat_path(combat_id: str | None = None) -> str:
    """Given a combat ID, get it's filepath

    Args:
        combat_id (`str`, optional): Combat ID. Defaults to None.

    Returns:
        `str`: Path to saved combat file
    """
    return SAVED_COMBAT_DIR + f"/{combat_id}.json" if combat_id else LIVE_COMBAT_PATH


def get_combat_list() -> list[str]:
    """Get list of saved combat files

    Returns:
        `list[str]`: List of combat files
    """
    combat_files = os.listdir(SAVED_COMBAT_DIR)
    filenames = [f.removesuffix(".json") for f in combat_files]
    return filenames


class CombatClient:
    """Class to manage a combat encounter"""

    def __init__(self: "CombatClient") -> None:
        """Init Combat"""
        self.combat_data: CombatData = list()

    async def __load_combat__(self: "CombatClient", combat_id: str | None = None) -> None:
        """Load a combat file

        Args:
            combat_id (`str`, optional): ID of the combat to load. If None, load default combat file. Defaults to None.
        """
        combat_path = get_combat_path(combat_id)
        raw_combat_data = await read_json_async(combat_path)
        self.combat_data = [load_character_from_file(c) for c in raw_combat_data]

    async def __save_combat__(self: "CombatClient", combat_id: str | None = None) -> None:
        """Save combat data to a file

        Args:
            combat_id (`str`, optional): ID of the combat to save. If None, save to default combat file. Defaults to None.
        """
        combat_path = get_combat_path(combat_id)
        combat_data_json = [asdict(c) for c in self.combat_data]
        await write_json_async(combat_path, combat_data_json)

    async def __clear_combat__(self: "CombatClient") -> None:
        """Clear combat data and start fresh.

        Existing data will be saved to a "backup" file.
        """
        # Load active combat into memory
        await self.__load_combat__()
        # Backup existing combat before clearing *just in case*
        await self.__save_combat__("backup")
        # Clear combat in memory
        self.combat_data = list()
        # Save new (empty) combat to default file
        await self.__save_combat__()

    async def begin(self: "CombatClient", combat_id: str | None = None) -> Embed:
        """Initiate a combat encounter.

        If preset provided, load encounter from file.
        Otherwise, start new encounter.

        Args:
            combat_id (`str`, optional): ID of the combat to load. Defaults to None.

        Returns:
            `Embed`: Discord Embed representing a combat encounter
        """
        # Clear existing combat
        await self.__clear_combat__()
        # Load combat data
        await self.__load_combat__(combat_id)
        # Save combat to "active" file
        await self.__save_combat__()
        # Create embed to send
        return get_combat_embed(self.combat_data)

    async def save(self: "CombatClient", combat_id: str) -> str:
        """Save combat

        Args:
            combat_id (`str`): ID of combat to save

        Returns:
            `str`: Path of the saved combat file
        """
        # Load current combat into memory
        await self.__load_combat__()
        # Save combat to specified file
        await self.__save_combat__(combat_id)
        # Return saved path
        return get_combat_path(combat_id)

    async def load(self: "CombatClient", combat_id: str) -> Embed:
        """Load combat

        Args:
            combat_id (`str`, optional): ID of the combat to load

        Returns:
            `Embed`: Discord Embed representing the loaded encounter
        """
        # TODO: If combat_id is none, list saved IDs?
        # Load saved combat into memory
        await self.__load_combat__(combat_id)
        # Save to "active" file
        await self.__save_combat__()
        # Generate embed
        return get_combat_embed(self.combat_data)

    def list(self: "CombatClient") -> Embed:
        """List saved combats

        Returns:
            `Embed`: Discord embed with list of saved encounters
        """
        # List existing encounters
        encounters = get_combat_list()
        return Embed(title="Saved Encounters:", description="\n".join(encounters))

    async def clear(self: "CombatClient") -> None:
        """Clear combat"""
        await self.__clear_combat__()

    async def show(self: "CombatClient", as_text: bool = False) -> Embed:
        """Show combat"""
        # Load active combat into memory
        await self.__load_combat__()
        # Generate embed
        return get_combat_embed(self.combat_data, as_text)

    async def add(self: "CombatClient", char_dict: RAW_CHAR_DICT_TYPE) -> None:
        """Add a player character to the encounter

        Args:
            char_dict (`dict`): Dict of character data
        """
        # Create Character object
        character = load_character_from_args(char_dict, "pc")

        # load active combat into memory
        await self.__load_combat__()

        # add character to data
        self.combat_data.append(character)

        # save to file
        await self.__save_combat__()

    async def madd(self: "CombatClient", char_dict: dict[str, str | int | bool]) -> None:
        """Add a non-player character (monster) to the encounter

        Args:
            char_dict (`dict`): Dict of character data
        """
        # Create Character object
        character = load_character_from_args(char_dict, "npc")

        await self.__load_combat__()

        # Add NPC to data
        self.combat_data.append(character)

        # Save to file
        await self.__save_combat__()

    async def update(self: "CombatClient", char_dict: dict[str, str | int | bool]) -> str:
        """Update an existing character (PC or NPC)

        Args:
            char_dict (`dict`): Dict of character data

        Returns:
            `str`: Response to send to context
        """
        # Load combat
        await self.__load_combat__()

        name = char_dict.pop("name")

        # TODO: placeholder string confirmation for basedpyright
        # Will remove this once I've implemented character schema validation
        if not isinstance(name, str):
            return f"Name must be a string, instead got {type(name)}: {name}"

        # Set default response
        response = f"Could not find character `{name}`"

        # Get character by name
        # TODO: support get by character ID
        for character in self.combat_data:
            if character.name.lower() == name.lower():
                update_character_from_args(character, char_dict)
                response = f"Updated character `{name}`"
                break

        # Save to file
        await self.__save_combat__()
        return response

    async def remove(self: "CombatClient", name: str) -> str:
        """Remove a character from combat (PR or NPC)

        Args:
            name (`str`): Name of the character to remove

        Returns:
            `str`: Response to send to context
        """
        # Load combat
        await self.__load_combat__()

        # Try to find matching character
        character_to_remove = None
        for character in self.combat_data:
            if character.name.lower() == name.lower():
                character_to_remove = character
                break

        # If found, remove character
        # Otherwise, exit
        if character_to_remove:
            self.combat_data.remove(character_to_remove)
        else:
            return f"Could not find character `{name}`"

        # Save to file
        await self.__save_combat__()
        return f"Removed character `{name}`"

    async def heal(self: "CombatClient", name: str, amount: int) -> str:
        """Heal an existing character (PC only)

        Args:
            amount (`int`): Amount to heal character

        Returns:
            `str`: Response to send to context
        """
        # Load combat
        await self.__load_combat__()

        response = f"Could not find character `{name}`"

        # Get character by name (TODO: support character ID)
        for character in self.combat_data:
            if character.name.lower() == name.lower():
                new_hp = character.hp.current + amount
                update_pc(character, "chp", new_hp)
                response = f"Updated character `{name}` - HP: {new_hp}"
                break

        # Save to file
        await self.__save_combat__()
        return response

    async def dmg(self: "CombatClient", name: str, amount: int) -> str:
        """Damage an existing character (PC only)

        Args:
            amount (`int`): Amount to heal character

        Returns:
            `str`: Response to send to context
        """
        # Load combat
        await self.__load_combat__()

        response = f"Could not find character `{name}`"

        # Get character by name (TODO: support character ID)
        for character in self.combat_data:
            if character.name.lower() == name.lower():
                new_hp = character.hp.current - amount
                update_pc(character, "chp", new_hp)
                response = f"Updated character `{name}` - HP: {new_hp}"
                break

        # Save to file
        await self.__save_combat__()
        return response
