"""Combat Commands"""

import argparse
import os
from typing import Any

from discord.ext.commands import Bot, Cog, Context, command

from utils.argparse_utils import ArgParseError
from utils.combat.args import CombatArgs, get_combat_args
from utils.combat.client import CombatClient
from utils.embed import create_error_embed
from utils.logging import get_logger

LOGGER = get_logger(os.path.basename(__file__))


######################
## COMBAT FUNCTIONS ##
######################


async def begin_combat(
    ctx: Context[Bot],
    combat_client: CombatClient,
    combat_args: CombatArgs,
) -> None:
    """Begin a new combat encounter, or load a saved encounter

    Args:
        ctx (`Context[Bot]`): Message context object from Discord
        combat_client (`CombatClient`): Combat client
        combat_args (`CombatArgs`): Command arguments with ID of combat to load. If ommitted, a new encounter will be started.
    """
    response = await combat_client.begin(combat_args.combat_id)
    await ctx.send(embed=response)


async def save_combat(
    ctx: Context[Bot],
    combat_client: CombatClient,
    combat_args: CombatArgs,
) -> None:
    """Save current combat encounter

    Args:
        ctx (`Context[Bot]`): Message context object from Discord
        combat_client (`CombatClient`): Combat client
        combat_args (`CombatArgs`): Command arguments with ID of combat to save
    """
    combat_path = await combat_client.save(combat_args.combat_id)
    response = f"Saved combat to `{combat_path}`"
    await ctx.send(response)


async def load_combat(
    ctx: Context[Bot],
    combat_client: CombatClient,
    combat_args: CombatArgs,
) -> None:
    """Load a saved combat encounter

    Args:
        ctx (`Context[Bot]`): Message context object from Discord
        combat_client (`CombatClient`): Combat client
        combat_args (`CombatArgs`): Command arguments with ID of combat to load. TODO: If ommitted, saved encounters will be listed.
    """
    response = await combat_client.load(combat_args.combat_id)
    await ctx.send(embed=response)


async def clear_combat(ctx: Context[Bot], combat_client: CombatClient, _: Any) -> None:  # pyright: ignore[reportExplicitAny]
    """Clear combat encounter

    Args:
        ctx (`Context[Bot]`): Message context object from Discord
        combat_client (`CombatClient`): Combat client
        combat_args (`CombatArgs`): Command arguments
    """
    await combat_client.clear()
    response = "Cleared currrent combat"
    await ctx.send(response)


async def show_combat(ctx: Context[Bot], combat_client: CombatClient, combat_args: CombatArgs) -> None:
    """Show the combat encounter.

    Args:
        ctx (`Context[Bot]`): Message context object from Discord
        combat_client (`CombatClient`): Combat client
        combat_args (`CombatArgs`): Command arguments
    """
    response = await combat_client.show(combat_args.as_text)
    await ctx.send(embed=response)


async def list_encounters(ctx: Context[Bot], combat_client: CombatClient, _: Any) -> None:  # pyright: ignore[reportExplicitAny]
    """List the saved combat encounters.

    Args:
        ctx (`Context[Bot]`): Message context object from Discord
        combat_client (`CombatClient`): Combat client
        combat_args (`CombatArgs`): Command arguments
    """
    response = combat_client.list()
    await ctx.send(embed=response)


async def add_character(ctx: Context[Bot], combat_client: CombatClient, combat_args: CombatArgs) -> None:
    """Add a player character to the encounter

    Args:
        ctx (`Context[Bot]`): Message context object from Discord
        combat_client (`CombatClient`): Combat client
        combat_args (`CombatArgs`): Command arguments with character data
    """
    char_dict = combat_args.__dict__
    # Remove the sub_command item from the dict
    del char_dict["sub_command"]
    await combat_client.add(char_dict)
    response = f"Added PC `{combat_args.name}`"
    await ctx.send(response)


async def add_monster(ctx: Context[Bot], combat_client: CombatClient, combat_args: CombatArgs) -> None:
    """Add a non-player character to the encounter

    Args:
        ctx (`Context[Bot]`): Message context object from Discord
        combat_client (`CombatClient`): Combat client
        combat_args (`CombatArgs`): Command arguments with character data
    """
    char_dict = combat_args.__dict__
    # Remove the sub_command item from the dict
    del char_dict["sub_command"]
    await combat_client.madd(char_dict)
    response = f"Added NPC `{combat_args.name}`"
    await ctx.send(response)


async def update_character(ctx: Context[Bot], combat_client: CombatClient, combat_args: CombatArgs) -> None:
    """Update an existing character

    Args:
        ctx (`Context[Bot]`): Message context object from Discord
        combat_client (`CombatClient`): Combat client
        combat_args (`CombatArgs`): Command arguments with character data
    """
    char_dict = combat_args.__dict__
    # Remove the sub_command item from the dict
    del char_dict["sub_command"]
    response = await combat_client.update(char_dict)
    await ctx.send(response)


async def remove_character(ctx: Context[Bot], combat_client: CombatClient, combat_args: CombatArgs) -> None:
    """Remove a character from the encounter

    Args:
        ctx (`Context[Bot]`): Message context object from Discord
        combat_client (`CombatClient`): Combat client
        combat_args (`CombatArgs`): Command arguments with character data
    """
    response = await combat_client.remove(combat_args.name)
    await ctx.send(response)


async def heal_character(ctx: Context[Bot], combat_client: CombatClient, combat_args: CombatArgs) -> None:
    """Heal a character

    Args:
        ctx (`Context[Bot]`): Message context object from Discord
        combat_client (`CombatClient`): Combat client
        combat_args (`CombatArgs`): Command arguments with character data
    """
    response = await combat_client.heal(combat_args.name, combat_args.amount)
    await ctx.send(response)


async def damage_character(ctx: Context[Bot], combat_client: CombatClient, combat_args: CombatArgs) -> None:
    """Heal a character

    Args:
        ctx (`Context[Bot]`): Message context object from Discord
        combat_client (`CombatClient`): Combat client
        combat_args (`CombatArgs`): Command arguments with character data
    """
    response = await combat_client.dmg(combat_args.name, combat_args.amount)
    await ctx.send(response)


###############
## COG SETUP ##
###############

COMBAT_COMMAND_CALLABLE_MAP = {
    "begin": begin_combat,
    "save": save_combat,
    "load": load_combat,
    "clear": clear_combat,
    "show": show_combat,
    "list": list_encounters,
    "add": add_character,
    "madd": add_monster,
    "update": update_character,
    "rm": remove_character,
    "heal": heal_character,
    "dmg": damage_character,
}


class Combat(Cog):
    """Cog defining commands related to combat"""

    def __init__(self: "Combat", bot: Bot) -> None:
        """Init Cog

        Args:
            bot (`Bot`): Discord Bot object
        """
        self.bot: Bot = bot

    @command(name="combat", help="Handle combat related tasks")
    async def handle_combat(self: "Combat", ctx: Context[Bot], *args: str) -> None:
        """Begin a new combat encounter, or load a saved encounter

        Args:
            ctx (`Context[Bot]`): Message context object from Discord
        """
        try:
            no_em_dash = [arg.replace("—", "--") for arg in args]
            combat_args = get_combat_args(*no_em_dash)
        except (ArgParseError, argparse.ArgumentError, argparse.ArgumentTypeError) as error:
            LOGGER.exception(error, exc_info=error)
            embed = create_error_embed(error, multiline=True)
            await ctx.send(embed=embed)
            return

        try:
            command_callable = COMBAT_COMMAND_CALLABLE_MAP[combat_args.sub_command]
        except KeyError as error:
            response = "should not have gotten here...."
            await ctx.send(response)
            LOGGER.exception(error, exc_info=error)
            embed = create_error_embed(error)
            await ctx.send(embed=embed)
            return

        combat_client = CombatClient()
        await command_callable(ctx, combat_client, combat_args)


async def setup(bot: Bot) -> None:
    """Setup Cog

    Args:
        bot (`Bot`): Discord Bot object
    """
    await bot.add_cog(Combat(bot))
