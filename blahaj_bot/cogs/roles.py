import asyncio
from collections import defaultdict
import logging

import discord
from discord import PartialEmoji, SlashCommandGroup, Emoji, Message, Role, Webhook, Interaction
from discord.ext import commands

from blahaj_bot import BotClient

logger = logging.getLogger(__name__)

class AssignableRole:
    def __init__(self, server_id: int, role_id: int, emoji: PartialEmoji|Emoji|str, role_msg_id: int):
        self.role_id = role_id
        self.role_msg_id = role_msg_id
        self.server_id = server_id

        if isinstance(emoji, str):
            self.emoji = PartialEmoji(name=emoji)
        elif isinstance(emoji, PartialEmoji):
            self.emoji = emoji
        else:
            self.emoji = PartialEmoji(name=emoji.name, animated=emoji.animated, id=emoji.id)

    def __str__(self) -> str:
        return f'Emoji: {self.emoji} - Role Message ID: {self.role_msg_id} - Role ID: {self.role_id} - Server ID: {self.server_id}'
    
    def encode(self):
        return {'type': "AssignableRole", 
                'role_id': self.role_id, 
                'role_msg_id': self.role_msg_id, 
                'server_id': self.server_id, 
                'emoji': {'type': "PartialEmoji", 
                          'name': self.emoji.name,
                          'id': self.emoji.id,
                          'animated': self.emoji.animated},
                'version': 1}
    
    @classmethod
    def decode(cls, data):
        assert data['version'] == 1
        return cls(data['server_id'], data['role_id'], PartialEmoji(name=data['emoji']['name'], animated=data['emoji']['animated'], id=data['emoji']['id']), data['role_msg_id'])
        
assignable_roles: list[AssignableRole] = list()
mappings: dict[int, dict[int, dict[PartialEmoji, AssignableRole]]] = dict() # server id -> message id -> emoji -> role

async def process_add_role(bot: BotClient, role: Role, emoji: Emoji|str, msg: Message, interaction: Interaction):
    ar = AssignableRole(msg.guild.id, role.id, emoji, msg.id)
    logger.info(f'Add Assignable Role: {ar}')
    assignable_roles.append(ar)

    if ar.server_id not in mappings:
        mappings[ar.server_id] = dict()
    if ar.role_msg_id not in mappings[ar.server_id]:
        mappings[ar.server_id][ar.role_msg_id] = dict()

    if ar.emoji in mappings[ar.server_id][ar.role_msg_id]:
        await interaction.followup.edit_message(interaction.message.id, content=f"Cannot add emoji: {emoji} for {role}. Message already uses that emoji", view=None)
        return

    # Add to persistence
    serverdb = bot.db[str(ar.server_id)]
    rolescol = serverdb["roles"]
    result = rolescol.replace_one({"role_id" : ar.role_id, "role_msg_id": ar.role_msg_id}, ar.encode(), upsert=True)
    if not result.acknowledged:
        await interaction.followup.edit_message(interaction.message.id, content=f"An error has occurred.", view=None)
        return

    mappings[ar.server_id][ar.role_msg_id][ar.emoji] = ar
    await interaction.followup.edit_message(interaction.message.id, content=f"Added emoji: {emoji} for {role}.", view=None)
    await msg.add_reaction(emoji)

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
        await interaction.response.edit_message(content=f"Role selected: {select.values[0]}.\nReact to the original message to select the associated emoji.", view=None, delete_after=90)

        def check(reaction, user):
            return user == interaction.user

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

        await process_add_role(bot=self.bot, role=select.values[0], emoji=reaction.emoji, msg=self.msg, interaction=interaction)

class Roles(commands.Cog):
    def __init__(self, bot: BotClient):
        self.bot = bot

        dblist = self.bot.db.list_database_names()
        for name in dblist:
            serverdb = self.bot.db[name]
            if "roles" in serverdb.list_collection_names():
                rolescol = serverdb["roles"]
                for x in rolescol.find({"type":"AssignableRole"}):
                    ar = AssignableRole.decode(x)
                    logger.info(f'Load Assignable Role: {ar}')
                    assignable_roles.append(ar)
                    if ar.server_id not in mappings:
                        mappings[ar.server_id] = dict()
                    if ar.role_msg_id not in mappings[ar.server_id]:
                        mappings[ar.server_id][ar.role_msg_id] = dict()
                    mappings[ar.server_id][ar.role_msg_id][ar.emoji] = ar
                    

    role = SlashCommandGroup("role", "Role Management")
    
    @role.command(description="WIP")
    async def debug(self, ctx: discord.ApplicationContext):
        serverdb = self.bot.db[str(ctx.guild.id)]
        rolescol = serverdb["roles"]
        for x in rolescol.find():
            logger.info(f'{x}')
        await ctx.respond('WIP')

    @commands.message_command(name="Add Role-Reactions")
    @commands.guild_only()
    @discord.default_permissions(
        manage_roles=True,
    ) # Only if can manage roles
    async def add_role_reaction(self, ctx: discord.ApplicationContext, message: discord.Message):
        await ctx.respond("Add Role", view=AddRoleView(self.bot, message), delete_after=60, ephemeral=True)

    # https://github.com/Pycord-Development/pycord/blob/master/examples/reaction_roles.py
    @commands.Cog.listener("on_raw_reaction_add")
    async def process_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Gives a role based on a reaction emoji."""

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None or payload.guild_id not in mappings:
            # Make sure we're still in the guild, and it's cached.
            return

        # Make sure that the message the user is reacting to is the one we care about.
        if payload.message_id not in mappings[payload.guild_id]:
            return

        # If the emoji isn't the one we care about then exit as well.
        if payload.emoji not in mappings[payload.guild_id][payload.message_id]:
            return
        
        role_id = mappings[payload.guild_id][payload.message_id][payload.emoji].role_id

        role = guild.get_role(role_id)
        if role is None:
            # Make sure the role still exists and is valid.
            return

        try:
            # Finally, add the role.
            await payload.member.add_roles(role)
            logger.info(f'Added role {role} to {payload.member}')
        except discord.HTTPException:
            # If we want to do something in case of errors we'd do it here.
            pass

    @commands.Cog.listener("on_raw_reaction_remove")
    async def process_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """Removes a role based on a reaction emoji."""

        # Make sure we're still in the guild, and it's cached.
        guild = self.bot.get_guild(payload.guild_id)
        if guild is None or payload.guild_id not in mappings:
            return

        # Make sure that the message the user is reacting to is the one we care about.
        if payload.message_id not in mappings[payload.guild_id]:
            return

        # If the emoji isn't the one we care about then exit as well.
        if payload.emoji not in mappings[payload.guild_id][payload.message_id]:
            return
        
        role_id = mappings[payload.guild_id][payload.message_id][payload.emoji].role_id

        role = guild.get_role(role_id)
        if role is None:
            # Make sure the role still exists and is valid.
            return

        # The payload for `on_raw_reaction_remove` does not provide `.member`
        # so we must get the member ourselves from the payload's `.user_id`.
        member = guild.get_member(payload.user_id)
        if member is None:
            # Make sure the member still exists and is valid.
            return

        try:
            # Finally, remove the role.
            await member.remove_roles(role)
            logger.info(f'Removed role {role} from {member}')
        except discord.HTTPException:
            # If we want to do something in case of errors we'd do it here.
            pass

def setup(bot):
    bot.add_cog(Roles(bot)) # add the cog to the bot