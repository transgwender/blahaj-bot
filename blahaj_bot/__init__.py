from blahaj_bot.client import MyClient
import discord
import logging
import sys

logger = logging.getLogger(__name__)

def bot() -> None:

    logging.basicConfig(filename='blahaj.log', level=logging.INFO)

    logger.info(sys.argv[1], "Hello from blahaj-bot!!!")

    intents = discord.Intents.default()
    intents.message_content = True

    file = open(sys.argv[1], "r")
    TOKEN = file.read()
    file.close()

    client = MyClient(intents=intents)
    client.run(TOKEN)
