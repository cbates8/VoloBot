"""Combat Slash Commands"""

import random
from typing import Literal
from discord.ext.commands import Bot, Cog
from discord import app_commands, Interaction
from utils.combat.client import CombatClient
from utils.combat.character import construct_pc, construct_npc


class Combat(Cog):
    """Cog defining slash commands related to combat"""

    def __init__(self: "Combat", bot: Bot) -> None:
        """Init Cog

        Args:
            bot (`Bot`): Discord Bot object
        """
        self.bot: Bot = bot
        self.combat_client: CombatClient = CombatClient()

    # --------------------------------------------------------
    group: app_commands.Group = app_commands.Group(name="combat", description="...")
    # --------------------------------------------------------

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

    #####################
    # Combat management #
    #####################

    @group.command(name="begin", description="Create a fresh encounter, or start a saved encounter")
    async def _begin(self: "Combat", interaction: Interaction, encounter_id: str | None = None) -> None:
        """Generate a new encounter, or load a saved encounter

        Args:
            interaction (`Interaction`): Interaction object from Discord
            encounter_id (`str | None`): ID of encounter to load. If ommitted, a new encounter will be started.
        """
        response = await self.combat_client.begin(encounter_id)
        await interaction.response.send_message(embed=response)

    @group.command(name="save", description="Save current encounter")
    async def _save(self: "Combat", interaction: Interaction, encounter_id: str) -> None:
        """Save current encounter

        Args:
            interaction (`Interaction`): Interaction object from Discord
            encounter_id (`str`): ID of encounter to save
        """
        encounter_path = await self.combat_client.save(encounter_id)
        await interaction.response.send_message(f"Saved encounter to `{encounter_path}`")

    @group.command(name="load", description="Load a saved encounter")
    async def _load(self: "Combat", interaction: Interaction, encounter_id: str) -> None:
        """Save current encounter

        Args:
            interaction (`Interaction`): Interaction object from Discord
            encounter_id (`str`): ID of encounter to load
        """
        response = await self.combat_client.load(encounter_id)
        await interaction.response.send_message(embed=response)

    @group.command(name="clear", description="Clear current encounter")
    async def _clear(self: "Combat", interaction: Interaction) -> None:
        """Clear current encounter

        Args:
            interaction (`Interaction`): Interaction object from Discord
        """
        await self.combat_client.clear()
        await interaction.response.send_message("Cleared currrent encounter")

    @group.command(name="show", description="Display the current encounter")
    async def _show(self: "Combat", interaction: Interaction, as_text: bool = False) -> None:
        """Show current encounter

        Args:
            interaction (`Interaction`): Interaction object from Discord
            as_text (`bool`): Should format as text instead of structured embed. Defaults to `False`.
        """
        response = await self.combat_client.show(as_text)
        await interaction.response.send_message(embed=response)

    @group.command(name="list", description="List saved encounters")
    async def _list(self: "Combat", interaction: Interaction) -> None:
        """List saved encounters

        Args:
            interaction (`Interaction`): Interaction object from Discord
        """
        response = self.combat_client.list()
        await interaction.response.send_message(embed=response)

    ########################
    # Character management #
    ########################

    @group.command(name="add_character", description="Add a new PC")
    async def _add_character(  # noqa: PLR0913, PLR0917
        self: "Combat",
        interaction: Interaction,
        name: str,
        initiative: int | None = None,
        armor_class: int | None = None,
        current_hp: int | None = None,
        max_hp: int | None = None,
        temp_hp: int | None = None,
        condition_name: str | None = None,
        condition_duration: str | None = None,
    ) -> None:
        """Add a player character to the encounter

        Args:
            interaction (`Interaction`): Interaction object from Discord
            name (`str`): Character name
            initiative (`int | None`): Initiative (optional)
            armor_class (`int | None`): Armor class (optional)
            current_hp (`int | None`): Current hit points (optional)
            max_hp (`int | None`): Maximum hit points (optional)
            temp_hp (`int | None`): Temporary hit points (optional)
            condition_name (`str | None`): Condition name (optional)
            condition_duration (`str | None`): Condition duration (optional)
        """
        character = construct_pc(name, initiative, armor_class, current_hp, max_hp, temp_hp, condition_name, condition_duration)
        await self.combat_client.add(character)
        await interaction.response.send_message(f"Added PC `{character.name}`")

    @group.command(name="add_npc", description="Add a new NPC")
    async def _add_npc(  # noqa: PLR0913, PLR0917
        self: "Combat",
        interaction: Interaction,
        name: str,
        initiative: int | None = None,
        hp_hint: Literal["healthy", "bloodied", "dead"] | None = None,
        condition_name: str | None = None,
        condition_duration: str | None = None,
    ) -> None:
        """Add a player character to the encounter

        Args:
            interaction (`Interaction`): Interaction object from Discord
            name (`str`): Character name
            initiative (`int | None`): Initiative (optional)
            hp_hint (`Literal["healthy", "bloodied", "dead"] | None`): Hit points hint
            condition_name (`str | None`): Condition name (optional)
            condition_duration (`str | None`): Condition duration (optional)
        """
        character = construct_npc(name, initiative, hp_hint, condition_name, condition_duration)
        await self.combat_client.add(character)
        await interaction.response.send_message(f"Added NPC `{character.name}`")

    @group.command(name="update_character", description="Update a character")
    async def _update_character(  # noqa: PLR0913, PLR0917
        self: "Combat",
        interaction: Interaction,
        name: str,
        initiative: int | None = None,
        armor_class: int | None = None,
        current_hp: int | None = None,
        max_hp: int | None = None,
        temp_hp: int | None = None,
        hp_hint: Literal["healthy", "bloodied", "dead"] | None = None,
        condition_name: str | None = None,
        condition_duration: str | None = None,
    ) -> None:
        """Update an existing character

        Args:
            interaction (`Interaction`): Interaction object from Discord
            name (`str`): Character name
            initiative (`int | None`): Initiative (optional)
            armor_class (`int | None`): Armor class (optional)
            current_hp (`int | None`): Current hit points (optional)
            max_hp (`int | None`): Maximum hit points (optional)
            temp_hp (`int | None`): Temporary hit points (optional)
            hp_hint (`Literal["healthy", "bloodied", "dead"] | None`): Hit points hint
            condition_name (`str | None`): Condition name (optional)
            condition_duration (`str | None`): Condition duration (optional)
        """
        response = await self.combat_client.update(name, initiative, armor_class, current_hp, max_hp, temp_hp, hp_hint, condition_name, condition_duration)
        await interaction.response.send_message(response)

    @group.command(name="remove_character", description="Remove a character")
    async def _remove_character(self: "Combat", interaction: Interaction, name: str) -> None:
        """Remove a character

        Args:
            interaction (`Interaction`): Interaction object from Discord
            name (`str`): Character name
        """
        response = await self.combat_client.remove(name)
        await interaction.response.send_message(response)

    @group.command(name="heal_character", description="Heal a character")
    async def _heal_character(self: "Combat", interaction: Interaction, name: str, amount: int) -> None:
        """Heal a character

        Args:
            interaction (`Interaction`): Interaction object from Discord
            name (`str`): Character name
            amount (`int`): Amount to heal character
        """
        response = await self.combat_client.heal(name, amount)
        await interaction.response.send_message(response)

    @group.command(name="damage_character", description="Damage a character")
    async def _damage_character(self: "Combat", interaction: Interaction, name: str, amount: int) -> None:
        """Damage a character

        Args:
            interaction (`Interaction`): Interaction object from Discord
            name (`str`): Character name
            amount (`int`): Amount to damage character
        """
        response = await self.combat_client.dmg(name, amount)
        await interaction.response.send_message(response)


async def setup(bot: Bot) -> None:
    """Setup Cog

    Args:
        bot (`Bot`): Discord Bot object
    """
    await bot.add_cog(Combat(bot))
