from blahaj_bot.client import MyClient
import discord
import os
import sys
from dotenv import load_dotenv

def bot() -> None:
    print(sys.argv[1], "Hello from blahaj-bot!!!")

    intents = discord.Intents.default()
    intents.message_content = True

    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')

    client = MyClient(intents=intents)
    client.run(TOKEN)
