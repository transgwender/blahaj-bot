from blahaj_bot.client import MyClient
import discord
import sys

def bot() -> None:
    print(sys.argv[1], "Hello from blahaj-bot!!!")

    intents = discord.Intents.default()
    intents.message_content = True

    file = open(sys.argv[1], "r")
    TOKEN = file.read()
    file.close()

    client = MyClient(intents=intents)
    client.run(TOKEN)
