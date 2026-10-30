"""Spell Commands"""

from typing import Literal
from discord import Embed
from discord.ext.commands import Bot, Cog, Context, command, parameter

from utils.spell import get_spell


class Spell(Cog):
    """Cog defining commands related to spellcasting"""

    def __init__(self: "Spell", bot: Bot) -> None:
        """Init Cog

        Args:
            bot (`Bot`): Discord Bot object
        """
        self.bot: Bot = bot

    @command(name="spell", help="Search spell descriptions")
    async def send_spell_description(
        self: "Spell",
        ctx: Context[Bot],
        spell_name: str = parameter(description="The name of the spell to search for"),
        source: Literal["web", "local", "all"] = parameter(default="all", description="Source to get spell info from ('web' | 'local' | 'all')"),
    ) -> None:
        """Search for a spell and return its description

        Args:
            ctx (`Context`): Message context object from Discord
            spell_name (`str`): The name of the spell to search for
            source (`str`, optional): The source to check for spell info. Defaults to 'all'
        """
        response = await get_spell(spell_name, source)
        if isinstance(response, Embed):
            await ctx.send(embed=response)
        else:
            await ctx.send(response)


async def setup(bot: Bot) -> None:
    """Setup Cog

    Args:
        bot (`Bot`): Discord Bot object
    """
    await bot.add_cog(Spell(bot))
