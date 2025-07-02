import logging
import discord
from discord.ext import commands

from typing import Any, Mapping
from backloggery import BacklogClient
from pymongo import MongoClient

from blahaj_bot import __version__

logger = logging.getLogger(__name__)

class BotClient(commands.Bot):

    def __init__(self, *,
                 db: MongoClient[Mapping[str, Any]],
                 command_prefix,
                 backlog: BacklogClient,
                 intents: discord.Intents, **options: Any):
        super().__init__(command_prefix=command_prefix, intents=intents, **options)
        self.db = db
        self.backlog = backlog
        
        logger.info(f'Initializing cogs')
        super().load_extension('blahaj_bot.cogs.basic')
        # super().load_extension('blahaj_bot.cogs.roles')
        super().load_extension('blahaj_bot.cogs.backlog')
        logger.info(f'Cogs initialized')


    async def on_ready(self):
        logger.info(f'Logged on as {self.user}! - Version {__version__}')