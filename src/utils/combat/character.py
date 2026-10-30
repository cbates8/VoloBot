"""Combat Data Structures"""

import os
from dataclasses import dataclass
from typing import Literal

from utils.logging import get_logger
from utils.combat.types import RAW_CHAR_DICT_TYPE, PARSED_CHAR_DICT_TYPE

LOGGER = get_logger(os.path.basename(__file__))

###############
# Dataclasses #
###############


@dataclass
class HitPoints:
    """Dataclass representing character hit points"""

    current: int = None
    max: int | None = None
    temp: int | None = None
    hint: str | None = None


@dataclass
class Condition:
    """Dataclass representing character condition"""

    name: str = None
    duration: str = None


@dataclass
class Character:
    """Dataclass representing a character"""

    name: str
    hp: HitPoints
    conditions: list[Condition]
    type: Literal["pc", "npc"]
    id: str = None
    initiative: int = None
    ac: int = None


#########
# Utils #
#########


# Type Alias
CombatData = list[Character]


def load_character_from_file(char_dict: PARSED_CHAR_DICT_TYPE) -> Character:
    """Load character object from dict

    Args:
        char_dict (`dict`): Dict representing a character

    Returns:
        `Character`: Character object
    """
    # Get HP object
    hp_dict = char_dict.pop("hp", None)
    hp = HitPoints(**hp_dict)

    # Get list of Condition objects
    conditions_list = char_dict.pop("conditions", None)
    conditions = [Condition(**condition_dict) for condition_dict in conditions_list]

    # Get final Character object
    return Character(**char_dict, hp=hp, conditions=conditions)


def load_character_from_args(char_dict: RAW_CHAR_DICT_TYPE, char_type: Literal["pc", "npc"]) -> Character:
    """Load character object from dict

    Args:
        char_dict (`dict`): Dict representing a character
        char_type (`Literal["pc", "npc"]`): Type of character to create

    Returns:
        `Character`: Character object
    """
    # Get HP object
    if char_type == "pc":
        current_hp = char_dict.pop("chp", None)
        max_hp = char_dict.pop("mhp", None)
        hp = HitPoints(current=current_hp, max=max_hp)
    else:
        is_h = char_dict.pop("h")
        is_b = char_dict.pop("b")
        is_d = char_dict.pop("d")
        if is_h:
            hp_hint = "Healthy"
        elif is_b:
            hp_hint = "Bloodied"
        elif is_d:
            hp_hint = "Dead"
        else:
            hp_hint = None
        hp = HitPoints(hint=hp_hint)

    # Get list of Condition objects
    condition_name = char_dict.pop("cn", None)
    condition_duration = char_dict.pop("cd", None)
    conditions = [Condition(name=condition_name, duration=condition_duration)]

    # Get final Character object
    return Character(**char_dict, hp=hp, conditions=conditions, type=char_type)


def update_pc(character: Character, field: str, value: str | int | None) -> None:
    """Update a player character

    Args:
        character (`Character`): Character to update
        field (`str`): Field to update
        value (`str | int | None`): New value
    """
    if field == "chp":
        character.hp.current = value
    elif field == "mhp":
        character.hp.max = value
    elif field == "ac":
        character.ac = value
    elif field == "initiative":
        character.initiative = value


def update_npc(character: Character, field: str, value: int | None) -> None:
    """Update a non-player character

    Args:
        character (`Character`): Character to update
        field (`str`): Field to update
        value (`int | None`): New value (only used for initiative)
    """
    if field == "h":
        character.hp.hint = "Healthy"
    elif field == "b":
        character.hp.hint = "Bloodied"
    elif field == "d":
        character.hp.hint = "Dead"
    elif field == "initiative":
        character.initiative = value


def update_condition(character: Character, condition_name: str, condition_duration: str = None) -> None:
    """Update a character condition or add a new one

    Args:
        character (`Character`): Character to update
        condition_name (`str`): Name of the condition to add or update
        condition_duration (`str`, optional): Description of the condition. Defaults to None.
    """
    # Update condition if it exists
    is_updated = False
    for c in character.conditions:
        if c.name.lower() == condition_name.lower():
            c.duration = condition_duration
            is_updated = True
            break

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


def update_character_from_args(character: Character, char_dict: RAW_CHAR_DICT_TYPE) -> None:
    """Update a character object

    Args:
        character (`Character`): Character to update
        char_dict (`dict`): Dict representing fields to update
    """
    # For set args, apply updates to existing character
    for key, value in char_dict.items():
        if character.type == "pc":
            update_pc(character, key, value)
        else:
            update_npc(character, key, value)

    # Add or update condition
    if condition_name := char_dict.get("cn"):
        update_condition(character, condition_name, char_dict.get("cd"))

    # Remove condition
    if condition_name := char_dict.get("crm"):
        remove_condition(character, condition_name)
