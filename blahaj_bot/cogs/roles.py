import asyncio
import logging

import discord
from discord import SlashCommandGroup, Emoji, Message, Role, Webhook, Interaction
from discord.ext import commands

from blahaj_bot import BotClient

logger = logging.getLogger(__name__)

async def process_add_role(role: Role, emoji: Emoji|str, msg: Message, interaction: Interaction):
    await interaction.followup.edit_message(interaction.id, content=f"Added emoji: {emoji} for {role}.", view=None)
    await msg.add_reaction(emoji)
    logger.info(f'Reaction Emoji: {emoji}, Role: {role}')

class AddRoleView(discord.ui.View):
    def __init__(self, bot: BotClient, msg: Message, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.bot = bot
        self.msg = msg

    @discord.ui.role_select(
        placeholder="Select a role!",
        min_values=1,
        max_values=1,
    )
    async def select_callback(self, select,
                              interaction: discord.Interaction):
        await interaction.response.edit_message(content=f"Role selected: {select.values[0]}.\nReact to this message to select associated emoji.", view=None, delete_after=90)

        def check(reaction, user):
            return user == self.msg.author

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=check)
        except asyncio.TimeoutError:
            await interaction.followup.edit_message(interaction.message.id, content=f"No emoji provided, cancelling.", view=None)
            return

        if not isinstance(reaction.emoji, str):
            e: Emoji | None = self.bot.get_emoji(reaction.emoji.id)
            if e is None or not e.is_usable():
                await interaction.followup.edit_message(interaction.message.id, content=f"Unavailable emoji selected.", view=None)
                return

        await process_add_role(role=select.values[0], emoji=reaction.emoji, msg=self.msg, interaction=interaction)

class Roles(commands.Cog):

    def __init__(self, bot: BotClient):
        self.bot = bot

    role = SlashCommandGroup("role", "Role Management")

    @role.command(description="WIP")
    async def debug(self, ctx: discord.ApplicationContext):
        serverdb = self.bot.db[str(ctx.guild.id)]
        rolescol = serverdb["roles"]
        result = rolescol.replace_one({"role": "debug"}, {"role": "debug"}, upsert=True)
        logger.info(f'{ctx.guild.name} -- {result}')
        for x in rolescol.find():
            logger.info(f'{x}')
        await ctx.respond('WIP')

    @commands.message_command(name="Add Role-Reactions")
    async def add_role_reaction(self, ctx: discord.ApplicationContext, message: discord.Message):
        await ctx.respond("Add Role", view=AddRoleView(self.bot, message), delete_after=60)

def setup(bot):
    bot.add_cog(Roles(bot)) # add the cog to the bot