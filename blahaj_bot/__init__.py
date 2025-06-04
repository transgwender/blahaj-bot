from blahaj_bot.client import MyClient
from pymongo import MongoClient
import discord
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

    file = open(sys.argv[1], "r")
    TOKEN = file.read()
    file.close()

    bot_client = MyClient(intents=intents)
    bot_client.run(TOKEN)

