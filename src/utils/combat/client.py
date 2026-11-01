"""Combat Utils"""

import os
from typing import Literal

from discord import Embed

from constants.paths import ACTIVE_ENCOUNTER_PATH, SAVED_ENCOUNTER_DIR
from utils.combat.models import Character
from utils.combat.character import construct_pc, construct_npc, get_character_by_name
from utils.combat.types import ENCOUNTER_TYPE
from utils.combat.formatting import get_encounter_embed
from utils.json_utils import read_json_async, write_json_async
from utils.logging import get_logger

LOGGER = get_logger(os.path.basename(__file__))


def get_encounter_path(encounter_id: str | None = None) -> str:
    """Get the filepath for a combat encounter. If no ID is given, get the path of the "active" encounter.

    Args:
        encounter_id (`str | None`): ID of the encounter to search for. Defaults to None.

    Returns:
        `str`: Path to saved encounter file
    """
    return SAVED_ENCOUNTER_DIR + f"/{encounter_id}.json" if encounter_id else ACTIVE_ENCOUNTER_PATH


def list_saved_encounters() -> list[str]:
    """Get list of saved encounters

    Returns:
        `list[str]`: List of encounter files
    """
    encounter_files = os.listdir(SAVED_ENCOUNTER_DIR)
    return [f.removesuffix(".json") for f in encounter_files]


class CombatClient:
    """Class to manage combat encounters"""

    def __init__(self: "CombatClient") -> None:
        """Init Combat"""
        self.active_encounter: ENCOUNTER_TYPE = list()

    async def __load_encounter__(self: "CombatClient", encounter_id: str | None = None) -> None:
        """Load an encounter file

        Args:
            encounter_id (`str`, optional): ID of the encounter to load. If None, load default encounter file. Defaults to None.
        """
        encounter_path = get_encounter_path(encounter_id)
        raw_encounter = await read_json_async(encounter_path)
        self.active_encounter = [Character(**raw_character) for raw_character in raw_encounter]

    async def __save_encounter__(self: "CombatClient", encounter_id: str | None = None) -> None:
        """Save encounter to a file

        Args:
            encounter_id (`str`, optional): ID of the encounter to save. If None, save to default encounter file. Defaults to None.
        """
        encounter_path = get_encounter_path(encounter_id)
        encounter_dump = [character.model_dump() for character in self.active_encounter]
        await write_json_async(encounter_path, encounter_dump)

    async def __clear_encounter__(self: "CombatClient") -> None:
        """Clear encounter data and start fresh.

        Existing data will be saved to a "backup" file.
        """
        # Load active encounter into memory
        await self.__load_encounter__()
        # Backup existing encounter before clearing *just in case*
        await self.__save_encounter__("backup")
        # Clear encounter in memory
        self.active_encounter = list()
        # Save new (empty) encounter to default file
        await self.__save_encounter__()

    async def begin(self: "CombatClient", encounter_id: str | None = None) -> Embed:
        """Initiate an encounter.

        If preset provided, load encounter from file.
        Otherwise, start new encounter.

        Args:
            encounter_id (`str`, optional): ID of the encounter to load. Defaults to None.

        Returns:
            `Embed`: Discord Embed representing an encounter
        """
        # Clear existing encounter
        await self.__clear_encounter__()
        # Load target encounter data
        await self.__load_encounter__(encounter_id)
        # Save encounter to "active" file
        await self.__save_encounter__()
        # Create embed to send
        return get_encounter_embed(self.active_encounter)

    async def save(self: "CombatClient", encounter_id: str) -> str:
        """Save encounter

        Args:
            encounter_id (`str`): ID of encounter to save

        Returns:
            `str`: Path of the saved encounter file
        """
        # Load current encounter into memory
        await self.__load_encounter__()
        # Save encounter to specified file
        await self.__save_encounter__(encounter_id)
        # Return saved path
        return get_encounter_path(encounter_id)

    async def load(self: "CombatClient", encounter_id: str) -> Embed:
        """Load encounter

        Args:
            encounter_id (`str`, optional): ID of the encounter to load

        Returns:
            `Embed`: Discord Embed representing the loaded encounter
        """
        # Load saved combat into memory
        await self.__load_encounter__(encounter_id)
        # Save to "active" file
        await self.__save_encounter__()
        # Generate embed
        return get_encounter_embed(self.active_encounter)

    def list(self: "CombatClient") -> Embed:
        """List saved combats

        Returns:
            `Embed`: Discord embed with list of saved encounters
        """
        encounters = list_saved_encounters()
        return Embed(title="Saved Encounters:", description="\n".join(encounters))

    async def clear(self: "CombatClient") -> None:
        """Clear encounter"""
        await self.__clear_encounter__()

    async def show(self: "CombatClient", as_text: bool = False) -> Embed:
        """Show encounter

        Args:
            as_text (`bool`): Should format as text instead of structured embed. Defaults to `False`.
        """
        # Load active encounter into memory
        await self.__load_encounter__()
        # Generate embed
        return get_encounter_embed(self.active_encounter, as_text)

    async def add(self: "CombatClient", character: Character) -> None:
        """Add a character to the encounter

        Args:
            character (`Character`): Character object to add
        """
        # load active encounter into memory
        await self.__load_encounter__()

        # add character to encounter data
        self.active_encounter.append(character)

        # save to file
        await self.__save_encounter__()

    async def update(  # noqa: PLR0913, PLR0917
        self: "CombatClient",
        name: str,
        initiative: int | None = None,
        armor_class: int | None = None,
        current_hp: int | None = None,
        max_hp: int | None = None,
        temp_hp: int | None = None,
        hp_hint: Literal["healthy", "bloodied", "dead"] | None = None,
        condition_name: str | None = None,
        condition_duration: str | None = None,
    ) -> str:
        """Update an existing character

        Args:
            name (`str`): Character name
            initiative (`int | None`): Initiative (optional)
            armor_class (`int | None`): Armor class (optional)
            current_hp (`int | None`): Current hit points (optional)
            max_hp (`int | None`): Maximum hit points (optional)
            temp_hp (`int | None`): Temporary hit points (optional)
            hp_hint (`Literal["healthy", "bloodied", "dead"] | None`): Hit points hint
            condition_name (`str | None`): Condition name (optional)
            condition_duration (`str | None`): Condition duration (optional)

        Returns:
            `str`: Response to send to context
        """
        # Load encounter
        await self.__load_encounter__()

        existing_character = get_character_by_name(self.active_encounter, name)

        # Return early if we can't find the character
        if not existing_character:
            return f"Could not find character `{name}`"

        # Create new character object containing updated fields
        update_character = (
            construct_pc(name, initiative, armor_class, current_hp, max_hp, temp_hp, condition_name, condition_duration)
            if existing_character.type == "pc"
            else construct_npc(name, initiative, hp_hint, condition_name, condition_duration)
        )

        # Get index of the existing character
        existing_character_index = self.active_encounter.index(existing_character)

        # Apply updates to the existing character
        self.active_encounter[existing_character_index] = existing_character.model_copy(update=update_character.model_dump(exclude_unset=True))

        # Save to file
        await self.__save_encounter__()
        return f"Updated character `{name}`"

    async def remove(self: "CombatClient", name: str) -> str:
        """Remove a character from the active encounter

        Args:
            name (`str`): Name of the character to remove

        Returns:
            `str`: Response to send to context
        """
        # Load encounter
        await self.__load_encounter__()

        # Try to find matching character
        character_to_remove = get_character_by_name(self.active_encounter, name)

        # Return early if we can't find the character
        if not character_to_remove:
            return f"Could not find character `{name}`"

        # Remove entry from active encounter
        self.active_encounter.remove(character_to_remove)

        # Save to file
        await self.__save_encounter__()
        return f"Removed character `{name}`"

    async def heal(self: "CombatClient", name: str, amount: int) -> str:
        """Heal an existing character (PC only)

        Args:
            name (`str`): Name of the character to heal
            amount (`int`): Amount to heal character

        Returns:
            `str`: Response to send to context
        """
        # Load encounter
        await self.__load_encounter__()

        existing_character = get_character_by_name(self.active_encounter, name)

        # Return early if we can't find the character
        if not existing_character:
            return f"Could not find character `{name}`"

        # Return early if character is an NPC
        if existing_character.type == "npc":
            return f"Character `{name}` is an NPC! Complain to my creator that this isn't implemented yet"

        # Return early if character doesn't have hp
        if not existing_character.hp or not existing_character.hp.current:
            return f"Character `{name}` does not have HP set..."

        new_hp = existing_character.hp.current + amount

        # Create new character object containing updated hp
        update_character = construct_pc(name, current_hp=new_hp)

        # Get index of the existing character
        existing_character_index = self.active_encounter.index(existing_character)

        # Apply updates to the existing character
        self.active_encounter[existing_character_index] = existing_character.model_copy(update=update_character.model_dump(exclude_unset=True))

        # Save to file
        await self.__save_encounter__()
        return f"Healed character `{name}` by {amount} points"

    async def dmg(self: "CombatClient", name: str, amount: int) -> str:
        """Damage an existing character (PC only)

        Args:
            name (`str`): Name of the character to heal
            amount (`int`): Amount to heal character

        Returns:
            `str`: Response to send to context
        """
        # Load encounter
        await self.__load_encounter__()
        existing_character = get_character_by_name(self.active_encounter, name)

        # Return early if we can't find the character
        if not existing_character:
            return f"Could not find character `{name}`"

        # Return early if character is an NPC
        if existing_character.type == "npc":
            return f"Character `{name}` is an NPC! Complain to my creator that this isn't implemented yet"

        # Return early if character doesn't have hp
        if not existing_character.hp or not existing_character.hp.current:
            return f"Character `{name}` does not have HP set..."

        new_hp = existing_character.hp.current - amount

        # Create new character object containing updated hp
        update_character = construct_pc(name, current_hp=new_hp)

        # Get index of the existing character
        existing_character_index = self.active_encounter.index(existing_character)

        # Apply updates to the existing character
        self.active_encounter[existing_character_index] = existing_character.model_copy(update=update_character.model_dump(exclude_unset=True))

        # Save to file
        await self.__save_encounter__()
        return f"Damaged character `{name}` by {amount} points"
