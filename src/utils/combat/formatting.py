"""Combat Formatting Utils"""

import os

from discord import Embed

from constants.colors import ANSI_WRAPPER, GREY_WRAPPER, NORMAL_WRAPPER, RED_WRAPPER
from utils.combat.types import ENCOUNTER_TYPE, BINNED_ENCOUNTER_TYPE
from utils.combat.models import Character, Condition, HitPoints
from utils.logging import get_logger

LOGGER = get_logger(os.path.basename(__file__))


###########################
### Indicator Constants ###
###########################

INDICATOR_WRAPPER = "- {body}\n"
## PC Indicator ##
# - Nibis Wickelhackle <8/12 HP> [AC 18] (Guidance - 5 turns)
HP_STRING = "<{current}/{max} HP>"  # TODO: Support for temp HP
AC_STRING = "[{ac} AC]"
CONDITION_DURATION = "- {duration}"
CONDITION_STRING = "{condition} {duration}"
CONDITION_WRAPPER = "({conditions})"
PC_STRING = "{name} {hp} {ac} {conditions}"

## Monster/NPC Indicator ##
# - Bugbear <Bloodied> (Frightened - 1 turn)
HEALTHY = "<😁>"
BLOODIED = "<🥵>"
DEAD = "<💀>"
NPC_HP_CONFIG = {
    "Healthy": {"display": HEALTHY, "format_wrapper": NORMAL_WRAPPER},
    "Bloodied": {"display": BLOODIED, "format_wrapper": RED_WRAPPER},
    "Dead": {"display": DEAD, "format_wrapper": GREY_WRAPPER},
    None: {"display": "", "format_wrapper": NORMAL_WRAPPER},
}
NPC_STRING = "{name} {hp} {conditions}"


####################
# Formatting Utils #
####################


def format_conditions(conditions: list[Condition]) -> str:
    """Format Character conditions

    Args:
        conditions (`list[Condition]`): List of conditions

    Returns:
        `str`: Formatted conditions string
    """
    parsed_conditions = [
        CONDITION_STRING.format(condition=cond.name, duration=CONDITION_DURATION.format(duration=cond.duration) if cond.duration else None)
        for cond in conditions
    ]
    return CONDITION_WRAPPER.format(conditions=", ".join(parsed_conditions)) if parsed_conditions else ""


def format_ac(ac: int | None) -> str:
    """Format Character armor class

    Args:
        ac (`int`): Armor class

    Returns:
        `str`: Formatted AC string
    """
    char_ac = ac if ac is not None else "??"
    return AC_STRING.format(ac=char_ac)


def format_pc_hp(hp: HitPoints) -> str:
    """Format Character hit points

    Args:
        hp (`HitPoints`): Hit points

    Returns:
        `str`: Formatted HP string
    """
    current_hp = hp.current if hp.current is not None else "??"  # pyright: ignore[reportUnnecessaryComparison]
    max_hp = hp.max if hp.max is not None else "??"
    return HP_STRING.format(current=current_hp, max=max_hp)


def format_pc(character: Character) -> str:
    """Format player character

    Args:
        character (`Character`): PC object

    Returns:
        `str`: Formatted PC string
    """
    # Format HP
    hp_string = format_pc_hp(character.hp) if character.hp else ""

    # Format AC
    ac_string = format_ac(character.ac)

    # Format Conditions
    conditions_string = format_conditions(character.conditions) if character.conditions else ""

    # Format final character string
    pc_str = PC_STRING.format(name=character.name, hp=hp_string, ac=ac_string, conditions=conditions_string)
    return INDICATOR_WRAPPER.format(body=pc_str)


def format_npc(character: Character) -> str:
    """Format non-player character

    Args:
        character (`Character`): NPC object

    Returns:
        `str`: Formatted NPC string
    """
    hp_config = NPC_HP_CONFIG[character.hp.hint if character.hp else None]

    # Format Conditions
    conditions_string = format_conditions(character.conditions) if character.conditions else ""

    npc_str = NPC_STRING.format(name=character.name, hp=hp_config["display"], conditions=conditions_string)
    formatted_str = hp_config["format_wrapper"].format(body=npc_str)

    return INDICATOR_WRAPPER.format(body=formatted_str)


def format_character(character: Character) -> str:
    """Format Character

    Args:
        character (`Character`): Character object

    Returns:
        `str`: Formatted Character string
    """
    if character.type == "pc":
        return format_pc(character)
    else:
        return format_npc(character)


###############
# Embed Utils #
###############


def bin_encounter_by_initiative(encounter: ENCOUNTER_TYPE) -> BINNED_ENCOUNTER_TYPE:
    """Organize combat into initiative bins. e.g. { 10: [Character, Character], ... }

    Args:
        encounter (`ENCOUNTER_TYPE`): Data to organize

    Returns:
        `BINNED_ENCOUNTER_TYPE`: Binned encounter data
    """
    binned_data: BINNED_ENCOUNTER_TYPE = dict()
    for character in encounter:
        i = character.initiative
        if i not in binned_data.keys():
            binned_data[i] = list()
        binned_data[i].append(character)
    return binned_data


def sort_binned_encounter(binned_encounter: BINNED_ENCOUNTER_TYPE) -> BINNED_ENCOUNTER_TYPE:
    """Sort binned encounter by initiative, descending.
    `None` should be at the bottom of the order, representing characters without initiative

    Args:
        binned_encounter (`BINNED_ENCOUNTER_TYPE`): Encounter data binned by initiative

    Returns:
        `BINNED_ENCOUNTER_TYPE`: Encounter data sorted by initiative
    """
    # lambda treats `None` as zero for comparisons
    return dict(sorted(binned_encounter.items(), key=lambda item: item[0] if item[0] is not None else 0, reverse=True))


def get_structured_encounter(binned_encounter: BINNED_ENCOUNTER_TYPE) -> Embed:
    """Get encounter embed structured with fields

    Args:
        binned_encounter (`BINNED_ENCOUNTER_TYPE`): Encounter data binned by initiative

    Returns:
        `Embed`: Formatted embed
    """
    embed = Embed(title="Combat")
    # For each initiative bin,
    # format character strings and add embed field
    for initiative, characters in binned_encounter.items():
        body = ""
        for c in characters:
            body += format_character(c)

        value = ANSI_WRAPPER.format(body=body)

        embed.add_field(name=initiative, value=value, inline=False)
    return embed


def get_text_encounter(binned_encounter: BINNED_ENCOUNTER_TYPE) -> Embed:
    """Get encounter embed as text description

    Args:
        binned_encounter (`BINNED_ENCOUNTER_TYPE`): Encounter data binned by initiative

    Returns:
        `Embed`: Formatted embed
    """
    # For each initiative bin,
    # format character strings and add to embed description
    description = ""
    for initiative, characters in binned_encounter.items():
        # If character has an initiative, format them appropriately
        if initiative:
            body = f"{initiative} "
            for i, c in enumerate(characters):
                body += f"{(' ' * (2 - len(str(initiative)))) if i == 0 else (' ' * 3)}{format_character(c)}\n"
        # Otherwise, list characters without initiative at the end
        else:
            body = f"{initiative}\n"
            for c in characters:
                body += f"{format_character(c)}\n"
        description += body
    description = ANSI_WRAPPER.format(body=description)
    return Embed(title="Combat", description=description)


def get_encounter_embed(encounter: ENCOUNTER_TYPE, as_text: bool = False) -> Embed:
    """Format encounter data as a Discord embed

    Args:
        encounter (`ENCOUNTER_TYPE`): Encounter to format
        as_text (`bool`, optional): Should format as text. Defaults to False.

    Returns:
        `Embed`: Formatted embed
    """
    # Bin by initiative
    binned_encounter = bin_encounter_by_initiative(encounter)

    # Sort by initiative
    sorted_encounter = sort_binned_encounter(binned_encounter)

    if as_text:
        # Format initiative as a code block in the embed description
        return get_text_encounter(sorted_encounter)
    else:
        # Format initiative as a embed field for each turn
        return get_structured_encounter(sorted_encounter)
