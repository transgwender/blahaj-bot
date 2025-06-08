import json
import logging
from typing import List
from urllib.error import HTTPError

import discord
from discord.ext.commands import Context
from backloggery import BacklogClient, Game

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

async def search_library(backlog: BacklogClient, ctx: Context, argv: List[str]):
    if len(argv) < 2:
        await ctx.send("Not enough arguments")
        return
    username = argv[0]
    search = " ".join(argv[1:])
    if not is_json(search):
        await ctx.send("Invalid search syntax")
        return

    try:
        result = backlog.search_library(username=username, search_regex=search)
    except HTTPError as e:
        await ctx.send(f'HTTPError: {e}')
        return
    if len(result) == 0:
        await ctx.send("No results found")
        return
    await ctx.send(f'Results found: {len(result)}', embed=create_game_embed(result[0]))


async def command_backlog(backlog: BacklogClient, ctx: Context, argv: List[str]):
    if len(argv) == 0:
        await ctx.send("No subcommand specified")
        return
    subcommand = argv.pop(0)

    match subcommand:
        case "search":
            await search_library(backlog, ctx, argv)
        case _:
            await ctx.send("Unknown subcommand")