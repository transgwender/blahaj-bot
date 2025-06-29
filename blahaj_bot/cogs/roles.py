import logging

import discord
from discord import SlashCommandGroup, MessageCommand
from discord.ext import commands

from blahaj_bot import BotClient

logger = logging.getLogger(__name__)

class MyModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="Short Input"))
        self.add_item(discord.ui.InputText(label="Long Input", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Modal Results")
        embed.add_field(name="Short Input", value=self.children[0].value)
        embed.add_field(name="Long Input", value=self.children[1].value)
        await interaction.response.send_message(embeds=[embed])

class MyView(discord.ui.View):
    def __init__(self, bot: BotClient, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.bot = bot

    @discord.ui.role_select(
        placeholder="Select a role!",  # the placeholder text that will be displayed if nothing is selected
        min_values=1,  # the minimum number of values that must be selected by the users
        max_values=1,  # the maximum number of values that can be selected by the users
    )
    async def select_callback(self, select,
                              interaction: discord.Interaction):
        await interaction.response.edit_message(content=f"Role selected: {select.values[0]}.\nReact to this message to select associated emoji.", view=None)
        # await interaction.response.send_modal(MyModal(title="Modal via Button"))

        reaction, user = await self.bot.wait_for('reaction_add', timeout=60)

        await interaction.response.edit_message(content=f"Selected emoji: {reaction.emoji}")

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
        """Shows an example of a modal dialog being invoked from a slash command."""
        await ctx.respond("Add Role", view=MyView(self.bot))

def setup(bot):
    bot.add_cog(Roles(bot)) # add the cog to the bot