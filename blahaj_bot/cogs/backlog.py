import json
import logging
from urllib.error import HTTPError

import discord
from backloggery import Game
from discord import SlashCommand, SlashCommandGroup
from discord.ext import commands

from blahaj_bot import BotClient

logger = logging.getLogger(__name__)

def is_json(myjson):
  try:
    json.loads(myjson)
  except ValueError as e:
    return False
  return True

def create_game_embed(game: Game):
    embed = discord.Embed(title=game.title, description="" if game.notes is None else game.notes)
    if game.status is not None:
        embed.add_field(name="Status", value=str(game.status))
    if game.priority is not None:
        embed.add_field(name="Priority", value=str(game.priority))
    if game.platform_title is not None:
        embed.add_field(name="Platform", value=game.platform_title)
    if game.region is not None:
        embed.add_field(name="Region", value=str(game.region))
    if game.phys_digi is not None:
        embed.add_field(name="Format", value=str(game.phys_digi))
    if game.own is not None:
        embed.add_field(name="Ownership", value=str(game.own))
    if game.last_update is not None:
        embed.add_field(name="Last Updated", value=game.last_update)
    # for key, val in game.__dict__.items():
    #     if val is not None:
    #         embed.add_field(name=key, value=val)
    return embed

class Backlog(commands.Cog):

    def __init__(self, bot: BotClient):
        self.bot = bot

    backlog = SlashCommandGroup("backlog", "Unofficial Backloggery Integration")

    search_backlog = backlog.create_subgroup("search", "Search Backloggery")

    @search_backlog.command()
    async def search(self, ctx: commands.Context, username, *, search):
        if not is_json(search):
            await ctx.send("Invalid search syntax")
            return

        try:
            result = self.bot.backlog.search_library(username=username, search_regex=search)
        except HTTPError as e:
            await ctx.send(f'HTTPError: {e}')
            return
        if len(result) == 0:
            await ctx.send("No results found")
            return
        await ctx.send(f'Results found: {len(result)}', embed=create_game_embed(result[0]))

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        # if isinstance(error, commands.MissingRequiredArgument):
        #     await ctx.send("Unknown command.")
        await ctx.send(f'An error occurred: {error}')

def setup(bot):
    bot.add_cog(Backlog(bot)) # add the cog to the bot