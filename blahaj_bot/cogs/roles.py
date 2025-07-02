import asyncio
import logging

import discord
from discord import PartialEmoji, SlashCommandGroup, Emoji, Message, Role, Webhook, Interaction
from discord.ext import commands

from blahaj_bot import BotClient

logger = logging.getLogger(__name__)

class AssignableRole:
    def __init__(self, server_id: int, role_id: int, emoji: Emoji|str, role_msg_id: int):
        self.role_id = role_id
        self.role_msg_id = role_msg_id
        self.server_id = server_id

        if isinstance(emoji, str):
            self.emoji = PartialEmoji(name=emoji)
        else:
            self.emoji = PartialEmoji(name=emoji.name, animated=emoji.animated, id=emoji.id)

    def __str__(self) -> str:
        return f'Emoji: {self.emoji} - Role Message ID: {self.role_msg_id} - Role ID: {self.role_id} - Server ID: {self.server_id}'
        
assignable_roles: list[AssignableRole]
mappings: dict[int, dict[int, AssignableRole]]

async def process_add_role(role: Role, emoji: Emoji|str, msg: Message, interaction: Interaction):
    await interaction.followup.edit_message(interaction.message.id, content=f"Added emoji: {emoji} for {role}.", view=None)
    await msg.add_reaction(emoji)
    ar = AssignableRole(msg.guild.id, role.id, emoji, msg.id)
    logger.info(f'Add Assignable Role: {ar}')
    assignable_roles.append(ar)
    mappings[ar.server_id][ar.role_msg_id] = ar
    logger.info(f'{mappings}')

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

    # https://github.com/Pycord-Development/pycord/blob/master/examples/reaction_roles.py
    @commands.Cog.listener("on_raw_reaction_add")
    async def process_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Gives a role based on a reaction emoji."""
        logger.info(f'Reaction Added: {payload.emoji} to {payload.message_id} by {payload.user_id}')

    @commands.Cog.listener("on_raw_reaction_remove")
    async def process_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """Removes a role based on a reaction emoji."""
        logger.info(f'Reaction Removed: {payload.emoji} from {payload.message_id} by {payload.user_id}')

def setup(bot):
    bot.add_cog(Roles(bot)) # add the cog to the bot