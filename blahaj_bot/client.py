import discord
from logging import Logger
from typing import Any, Mapping
from backloggery import Game, BacklogClient
from discord import Intents
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

    async def on_message(self, message):
        self.logger.info(f'Message from {message.author}: {message.content}')

        if message.author == self.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')
        
        if message.content.startswith('$pat'):
            await message.channel.send('pat the pand')

        if message.content.startswith('$github'):
            await message.channel.send('Check out my source code at: https://github.com/transgwender/blahaj-bot')

        if message.content.startswith('$version'):
            await message.channel.send(f'Version {__version__}')

        if message.content.startswith('$role'):
            serverdb = self.db[str(message.guild.id)]
            rolescol = serverdb["roles"]
            result = rolescol.replace_one({"role" : "debug"}, { "role": "debug" }, upsert = True)
            self.logger.info(f'{message.guild.name} -- {result}')
            for x in rolescol.find():
                self.logger.info(f'{x}')
            await message.channel.send('WIP')