import logging

import discord
from discord import SlashCommandGroup, MessageCommand
from discord.ext import commands

from blahaj_bot import BotClient

logger = logging.getLogger(__name__)

class MyView(discord.ui.View):
    @discord.ui.role_select(
        placeholder="Select a role!",  # the placeholder text that will be displayed if nothing is selected
        min_values=1,  # the minimum number of values that must be selected by the users
        max_values=1,  # the maximum number of values that can be selected by the users
    )
    async def select_callback(self, select,
                              interaction):
        await interaction.response.send_message(f"{select.values[0]}")

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
        await ctx.respond("Choose a flavor!", view=MyView())

def setup(bot):
    bot.add_cog(Roles(bot)) # add the cog to the bot