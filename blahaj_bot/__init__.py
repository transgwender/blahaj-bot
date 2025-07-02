"""
Discord Bot
"""

__title__ = 'blahaj-bot'
__author__ = 'transgwender'
__version__ = '0.0.12'

import time
import aiohttp

from blahaj_bot.client import BotClient
from pymongo import MongoClient
from backloggery import BacklogClient
import discord
from discord.ext import commands
import logging
import sys

logger = logging.getLogger(__name__)

def bot() -> None:

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt="%(asctime)s %(name)s.%(levelname)s: %(message)s", datefmt="%Y.%m.%d %H:%M:%S")
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    file = open(sys.argv[1], "r")
    TOKEN = file.read()
    file.close()

    db_client = MongoClient('localhost', 27017)

    backlog_client = BacklogClient()

    bot_client = BotClient(db=db_client, command_prefix=commands.when_mentioned_or("$"), backlog=backlog_client, intents=intents)

    for i in range(3, 100):
        try:
            bot_client.run(TOKEN)
        except aiohttp.ClientConnectorError:
            logger.warning(f'Failed to connect, retrying in {i} seconds...')
            time.sleep(i)
        else:
            break