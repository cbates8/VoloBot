"""Combat Slash Commands"""

import random
from discord.ext.commands import Bot, Cog
from discord import app_commands, Interaction
from utils.combat.client import CombatClient


class CombatSlash(Cog):
    """Cog defining slash commands related to combat"""

    def __init__(self: "CombatSlash", bot: Bot) -> None:
        """Init Cog

        Args:
            bot (`Bot`): Discord Bot object
        """
        self.bot: Bot = bot

    # --------------------------------------------------------
    group: app_commands.Group = app_commands.Group(name="combat", description="...")
    # --------------------------------------------------------

    @app_commands.command(name="ping", description="...")
    async def _ping(self, interaction: Interaction):
        await interaction.response.send_message("pong!")

    @app_commands.command(name="echo", description="echo your message")
    async def _echo(self, interaction: Interaction, msg: str):
        result: list[str] = list()
        for char in msg:
            if char.isalpha():
                # Randomize or alternate case (using random choice here)
                if random.choice([True, False]):
                    result.append(char.upper())
                else:
                    result.append(char.lower())
            else:
                result.append(char)
        await interaction.response.send_message("".join(result))

    @group.command(name="show", description="...")
    async def _show(self, interaction: Interaction, as_text: bool = False):
        combat_client = CombatClient()
        response = await combat_client.show(as_text)
        await interaction.response.send_message(embed=response)


async def setup(bot: Bot) -> None:
    """Setup Cog

    Args:
        bot (`Bot`): Discord Bot object
    """
    await bot.add_cog(CombatSlash(bot))
