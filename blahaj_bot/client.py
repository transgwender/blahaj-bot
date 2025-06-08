import discord
from logging import Logger
from typing import Any, Mapping
from backloggery import Game, BacklogClient
from discord import Intents, Message
from pymongo import MongoClient

from blahaj_bot import __version__


class MyClient(discord.Client):

    def __init__(self, *,
                 logger: Logger,
                 db: MongoClient[Mapping[str, Any]],
                 backlog: BacklogClient,
                 intents: Intents, **options: Any):
        super().__init__(intents=intents, **options)
        self.logger = logger
        self.db = db
        self.backlog = backlog

    async def on_ready(self):
        self.logger.info(f'Logged on as {self.user}! - Version {__version__}')

    async def on_message(self, message: Message):
        self.logger.info(f'Message from {message.author}: {message.content}')

        if message.author == self.user or not message.content.startswith('$'):
            return

        incoming = message.content.replace('$', '').lower().strip().split()
        command = incoming.pop(0)

        match command:
            case "hello":
                await message.channel.send('Hello!')
            case "pat":
                await message.channel.send('pat the pand')
            case "github":
                await message.channel.send('Check out my source code at: https://github.com/transgwender/blahaj-bot')
            case "version":
                await message.channel.send(f'Version {__version__}')
            case "role":
                serverdb = self.db[str(message.guild.id)]
                rolescol = serverdb["roles"]
                result = rolescol.replace_one({"role" : "debug"}, { "role": "debug" }, upsert = True)
                self.logger.info(f'{message.guild.name} -- {result}')
                for x in rolescol.find():
                    self.logger.info(f'{x}')
                await message.channel.send('WIP')
            case "backloggery":
                await message.channel.send('WIP')
            case _:
                await message.channel.send('Unknown command')
