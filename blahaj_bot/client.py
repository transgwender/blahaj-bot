import logging
import discord

from typing import Any, Mapping
from backloggery import Game, BacklogClient
from pymongo import MongoClient

from blahaj_bot import __version__
from blahaj_bot.backlog import command_backlog
from blahaj_bot.role import command_role

logger = logging.getLogger(__name__)

class MyClient(discord.Client):

    def __init__(self, *,
                 db: MongoClient[Mapping[str, Any]],
                 backlog: BacklogClient,
                 intents: discord.Intents, **options: Any):
        super().__init__(intents=intents, **options)
        self.db = db
        self.backlog = backlog

    async def on_ready(self):
        logger.info(f'Logged on as {self.user}! - Version {__version__}')

    async def on_message(self, message: discord.Message):
        logger.info(f'Message from {message.author}: {message.content}')

        if message.author == self.user or not message.content.startswith('$'):
            return

        argv = message.content.replace('$', '').lower().strip().split()
        command = argv.pop(0)

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
                await command_role(db=self.db, message=message, argv=argv)
            case "backloggery" | "backlog":
                await command_backlog(backlog=self.backlog, message=message, argv=argv)
            case _:
                await message.channel.send('Unknown command')
