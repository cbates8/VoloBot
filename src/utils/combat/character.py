"""Combat Data Structures"""

import os
from typing import Literal

from utils.logging import get_logger
from utils.combat.types import ENCOUNTER_TYPE
from utils.combat.models import HitPoints, Condition, Character

LOGGER = get_logger(os.path.basename(__file__))


def get_character_by_name(encounter: ENCOUNTER_TYPE, name: str) -> Character | None:
    """Get character by name, or `None` if not found

    Args:
        encounter (`ENCOUNTER_TYPE`): Encounter data
        name (`str`): Name of character to find

    Returns:
        `Character | None`: Character object, or `None` if not found

    """
    for character in encounter:
        if character.name.lower() == name.lower():
            return character


def construct_pc(  # noqa: PLR0913, PLR0917
    name: str,
    initiative: int | None = None,
    armor_class: int | None = None,
    current_hp: int | None = None,
    max_hp: int | None = None,
    temp_hp: int | None = None,
    condition_name: str | None = None,
    condition_duration: str | None = None,
) -> Character:
    """Create a Player Character

    Args:
        name (`str`): Character name
        initiative (`int | None`): Initiative (optional)
        armor_class (`int | None`): Armor class (optional)
        current_hp (`int | None`): Current hit points (optional)
        max_hp (`int | None`): Maximum hit points (optional)
        temp_hp (`int | None`): Temporary hit points (optional)
        condition_name (`str | None`): Condition name (optional)
        condition_duration (`str | None`): Condition duration (optional)

    Returns:
        `Character`: Character object
    """
    # Create the HP object
    hp = HitPoints(current=current_hp, max=max_hp, temp=temp_hp)

    # Create the condition object
    conditions = [Condition(name=condition_name, duration=condition_duration)] if condition_name else None

    # Construct the final Character object
    return Character(name, type="pc", initiative=initiative, hp=hp, ac=armor_class, conditions=conditions)


def construct_npc(
    name: str,
    initiative: int | None = None,
    hp_hint: Literal["healthy", "bloodied", "dead"] | None = None,
    condition_name: str | None = None,
    condition_duration: str | None = None,
) -> Character:
    """Create a Non-Player Character

    Args:
        name (`str`): Character name
        initiative (`int | None`): Initiative (optional)
        hp_hint (`Literal["healthy", "bloodied", "dead"] | None`): Hit points hint
        condition_name (`str | None`): Condition name (optional)
        condition_duration (`str | None`): Condition duration (optional)

    Returns:
        `Character`: Character object
    """
    # Create the HP object
    hp = HitPoints(hint=hp_hint) if hp_hint else None

    # Create the condition object
    conditions = [Condition(name=condition_name, duration=condition_duration)] if condition_name else None

    # Construct the final Character object
    return Character(name, type="npc", initiative=initiative, hp=hp, conditions=conditions)


def update_condition(character: Character, condition_name: str, condition_duration: str = None) -> None:
    """Update a character condition or add a new one

    Args:
        character (`Character`): Character to update
        condition_name (`str`): Name of the condition to add or update
        condition_duration (`str`, optional): Description of the condition. Defaults to None.
    """
    # Update condition if it exists
    is_updated = False
    if character.conditions:
        for c in character.conditions:
            if c.name.lower() == condition_name.lower():
                c.duration = condition_duration
                is_updated = True
                break
    else:
        character.conditions = list()

    # Otherwise, add as new condition
    if not is_updated:
        character.conditions.append(Condition(name=condition_name, duration=condition_duration))


def remove_condition(character: Character, condition_name: str) -> None:
    """Remove a character condition

    Args:
        character (`Character`): Character to update
        condition_name (`str`): Name of the condition to remove
    """
    condition_to_remove = None
    for condition in character.conditions:
        if condition.name.lower() == condition_name:
            condition_to_remove = condition
            break

    if condition_to_remove:
        character.conditions.remove(condition_to_remove)
    else:
        LOGGER.info("Could not find condition `%s`", condition_name)
