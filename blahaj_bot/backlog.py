import json
import logging
from typing import List
from urllib.error import HTTPError

import discord
from discord import Message
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
    for key, val in game.__dict__.items():
        if val is not None:
            embed.add_field(name=key, value=val)
    return embed

async def search_library(backlog: BacklogClient, message: Message, argv: List[str]):
    if len(argv) < 2:
        await message.channel.send("Not enough arguments")
        return
    username = argv[0]
    search = " ".join(argv[1:])
    if not is_json(search):
        await message.channel.send("Invalid search syntax")
        return

    try:
        result = backlog.search_library(username=username, search_regex=search)
    except HTTPError as e:
        await message.channel.send(f'HTTPError: {e}')
        return
    if len(result) == 0:
        await message.channel.send("No results found")
        return
    await message.channel.send(f'Results found: {len(result)}', embed=create_game_embed(result[0]))


async def command_backlog(backlog: BacklogClient, message: Message, argv: List[str]):
    if len(argv) == 0:
        await message.channel.send("No subcommand specified")
        return
    subcommand = argv.pop(0)

    match subcommand:
        case "search":
            await search_library(backlog, message, argv)
        case _:
            await message.channel.send("Unknown subcommand")