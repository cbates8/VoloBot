"""Combat Formatting Utils"""

import os

from discord import Embed

from constants.colors import ANSI_WRAPPER, GREY_WRAPPER, NORMAL_WRAPPER, RED_WRAPPER
from utils.combat.character import Character, CombatData, Condition, HitPoints
from utils.logging import get_logger

LOGGER = get_logger(os.path.basename(__file__))


###########################
### Indicator Constants ###
###########################

INDICATOR_WRAPPER = "- {body}\n"
## PC Combat Indicator ##
# - Nibis Wickelhackle <8/12 HP> [AC 18] (Guidance - 5 turns)
HP_STRING = "<{current}/{max} HP>"  # TODO: Support for temp HP
AC_STRING = "[{ac} AC]"
CONDITION_DURATION = "- {duration}"
CONDITION_STRING = "{condition} {duration}"
CONDITION_WRAPPER = "({conditions})"
PC_STRING = "{name} {hp} {ac} {conditions}"

## Monster/NPC Combat Indicator ##
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
    hp_string = format_pc_hp(character.hp)

    # Format AC
    ac_string = format_ac(character.ac)

    # Format Conditions
    conditions_string = format_conditions(character.conditions)

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
    hp_config = NPC_HP_CONFIG[character.hp.hint]

    # Format Conditions
    conditions_string = format_conditions(character.conditions)

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


def bin_combat_by_initiative(combat_data: CombatData) -> dict[int, CombatData]:
    """Organize combat into initiative bins

    Args:
        combat_data (`CombatData`): Data to organize

    Returns:
        `dict[int, CombatData]`: Binned combat data
    """
    binned_data: dict[int, list[Character]] = dict()
    for c in combat_data:
        i = c.initiative
        if i not in binned_data.keys():
            binned_data[i] = list()

        binned_data[i] += [c]
    return binned_data


def get_structured_combat(data: dict[int, CombatData]) -> Embed:
    """Get combat embed structured with fields

    Args:
        data (`dict`): Combat data

    Returns:
        `Embed`: Formatted embed
    """
    embed = Embed(title="Combat")
    # For each initiative bin,
    # format character strings and add embed field
    for initiative, characters in data.items():
        body = ""
        for c in characters:
            body += format_character(c)

        value = ANSI_WRAPPER.format(body=body)

        embed.add_field(name=initiative, value=value, inline=False)
    return embed


def get_text_combat(data: dict[int, CombatData]) -> Embed:
    """Get combat embed as text description

    Args:
        data (`dict`): Combat data

    Returns:
        `Embed`: Formatted embed
    """
    # For each initiative bin,
    # format character strings and add to embed description
    description = ""
    for initiative, characters in data.items():
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


def get_combat_embed(combat_data: CombatData, as_text: bool = False) -> Embed:
    """Format combat data as a Discord embed

    Args:
        combat_data (`CombatData`): Combat data
        as_text (`bool`, optional): Should format as text. Defaults to False.

    Returns:
        `Embed`: Formatted embed
    """
    # Bin by initiative
    # { 10: [Character, Character], ... }
    binned_data = bin_combat_by_initiative(combat_data)

    # Sort by initiative (descending)
    # `None` should be at the bottom of the order,
    # lambda treats `None` as zero for comparisons
    sorted_data = dict(sorted(binned_data.items(), key=lambda item: item[0] if item[0] is not None else 0, reverse=True))  # pyright: ignore[reportUnnecessaryComparison]

    if as_text:
        # Format initiative as a code block in the embed description
        return get_text_combat(sorted_data)
    else:
        # Format initiative as a embed field for each turn
        return get_structured_combat(sorted_data)
