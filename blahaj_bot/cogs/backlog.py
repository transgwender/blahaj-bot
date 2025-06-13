import json
import logging
from datetime import datetime
from urllib.error import HTTPError

import discord
from backloggery import Game, NoDataFoundError, Priority, Region, PhysDigi
from backloggery.enums import Status, Own
from discord import SlashCommandGroup
from discord.ext import commands, pages

from blahaj_bot import BotClient

logger = logging.getLogger(__name__)

def is_json(myjson):
  try:
    json.loads(myjson)
  except ValueError as e:
    return False
  return True

def create_game_embed(timestamp: datetime, game: Game):
    embed = discord.Embed(title=game.title, description="" if game.notes is None else game.notes)
    if game.status is not None and str(game.status) is not "":
        embed.add_field(name="Status", value=str(game.status))
    if game.priority is not None and str(game.priority) is not "":
        embed.add_field(name="Priority", value=str(game.priority))
    if game.platform_title is not None and str(game.platform_title) is not "":
        embed.add_field(name="Platform", value=game.platform_title)
    if game.sub_platform_title is not None and str(game.sub_platform_title) is not "":
        embed.add_field(name="Sub-Platform", value=game.sub_platform_title)
    if game.region is not None and str(game.region) is not "":
        embed.add_field(name="Region", value=str(game.region))
    if game.phys_digi is not None and str(game.phys_digi) is not "":
        embed.add_field(name="Format", value=str(game.phys_digi))
    if game.own is not None and str(game.own) is not "":
        embed.add_field(name="Ownership", value=str(game.own))
    if game.achieve_score is not None and game.achieve_total is not None and game.achieve_total > 0:
        embed.add_field(name="Achievements", value=f"{game.achieve_score}/{game.achieve_total}")
    if game.last_update is not None and str(game.last_update) is not "":
        embed.add_field(name="Last Updated", value=game.last_update, inline=False)
    embed.set_footer(text=f'Last fetched: {timestamp.strftime("%Y-%m-%d %H:%M:%S")} - {timestamp.tzname()}')

    if game.has_review: # TODO: Review grab and embed
        review_embed = discord.Embed(title="Review")
        if game.rating is not None:
            review_embed.add_field(name="Rating", value=str(game.rating))
        return [embed, review_embed]
    return embed

class Backlog(commands.Cog):

    def __init__(self, bot: BotClient):
        self.bot = bot

    backlog = SlashCommandGroup("backlog", "Unofficial Backloggery Integration")

    search_backlog = backlog.create_subgroup("search", "Search Backlog")

    @search_backlog.command(description="Basic search")
    @discord.option("username", description="Username", input_type=str)
    @discord.option("title", description="Title", input_type=str, required=False)
    @discord.option("abbr", description="Console abbreviation", input_type=str, required=False)
    @discord.option("platform", description="Platform", input_type=str, required=False)
    @discord.option("status", description="Status", input_type=Status, required=False)
    @discord.option("priority", description="Priority", input_type=Priority, required=False)
    @discord.option("region", description="Region", input_type=Region, required=False)
    @discord.option("format", description="Format", input_type=PhysDigi, required=False)
    @discord.option("ownership", description="Ownership", input_type=Own, required=False)
    async def basic(self, ctx: discord.ApplicationContext, username, title, abbr, status, priority, platform, region, format, ownership):
        search = json.dumps({"title": f'(?i)^.*{title}.*$' if title is not None else '',
                             "abbr": f'(?i)^.*{abbr}.*$' if abbr is not None else '',
                             "platform_title": f'(?i)^.*{platform}.*$' if platform is not None else '',
                             "status": f'(?i)^.*{str(status)}.*$' if status is not None else '',
                             "priority": f'(?i)^.*{str(priority)}.*$' if priority is not None else '',
                             "region": f'(?i)^.*{str(region)}.*$' if region is not None else '',
                             "phys_digi": f'(?i)^.*{str(format)}.*$' if format is not None else '',
                             "own": f'(?i)^.*{str(ownership)}.*$' if ownership is not None else '',})

        logger.info(search)

        try:
            timestamp, result = self.bot.backlog.search_library(username=username, search_regex=search)
        except NoDataFoundError as e:
            await ctx.respond(f'NoDataFoundError: {e}')
            return
        except HTTPError as e:
            await ctx.respond(f'HTTPError: {e}')
            return
        if len(result) == 0:
            await ctx.respond("No results found")
            return

        if len(result) > 1000:
            await ctx.respond("More than 1000 results found, showing subset of results")
        res = list(map(lambda game : create_game_embed(timestamp, game), result[:1000]))
        paginator = pages.Paginator(pages=res, show_disabled=False, loop_pages=True)
        await paginator.respond(ctx.interaction, ephemeral=False)

    @search_backlog.command(description="Advanced search")
    @discord.option("username", description="Username", input_type=str)
    @discord.option("search", description="Search query in raw json", input_type=str, default="{}")
    async def advanced(self, ctx: discord.ApplicationContext, username, *, search):
        if not is_json(search):
            await ctx.respond("Invalid search syntax")
            return

        try:
            timestamp, result = self.bot.backlog.search_library(username=username, search_regex=search)
        except NoDataFoundError as e:
            await ctx.respond(f'NoDataFoundError: {e}')
            return
        except HTTPError as e:
            await ctx.respond(f'HTTPError: {e}')
            return
        if len(result) == 0:
            await ctx.respond("No results found")
            return

        if len(result) > 1000:
            await ctx.respond("More than 1000 results found, showing subset of results")
        res = list(map(lambda game : create_game_embed(timestamp, game), result[:1000]))
        paginator = pages.Paginator(pages=res, show_disabled=False, loop_pages=True)
        await paginator.respond(ctx.interaction, ephemeral=False)

def setup(bot):
    bot.add_cog(Backlog(bot)) # add the cog to the bot