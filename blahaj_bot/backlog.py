import json
import logging
from typing import List
from urllib.error import HTTPError

from discord import Message
from backloggery import BacklogClient

logger = logging.getLogger(__name__)

def is_json(myjson):
  try:
    json.loads(myjson)
  except ValueError as e:
    return False
  return True

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
    await message.channel.send(f'Results found: {len(result)} - First result: {result[0].title}')


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