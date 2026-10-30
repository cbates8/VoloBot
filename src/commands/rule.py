"""Rule Commands"""

from discord import Embed
from discord.ext.commands import Bot, Cog, Context, command, parameter

from utils.rules import get_rule


class Rule(Cog):
    """Cog defining commands related to rule lookup"""

    def __init__(self: "Rule", bot: Bot) -> None:
        """Init Cog

        Args:
            bot (`Bot`): Discord Bot object
        """
        self.bot: Bot = bot

    @command(name="rule", help="Search rule descriptions")
    async def send_rule_description(
        self: "Rule",
        ctx: Context[Bot],
        rule_name: str | None = parameter(default=None, description="The name of the rule to search for"),
    ) -> None:
        """Search for a rule and return its description

        Args:
            ctx (`Context`): Message context object from Discord
            rule_name (`str`, optional): The name of the rule to search for. If ommitted, known rules will be listed. Defaults to `None`.
        """
        response = await get_rule(rule_name)
        if isinstance(response, Embed):
            await ctx.send(embed=response)
        else:
            response = f"Could not find rule '{rule_name}' in your inventory."
            await ctx.send(response)


async def setup(bot: Bot) -> None:
    """Setup Cog

    Args:
        bot (`Bot`): Discord Bot object
    """
    await bot.add_cog(Rule(bot))
