import logging
import discord
from discord.ext import commands

from typing import Any, Mapping, List
from backloggery import Game, BacklogClient
from discord.ext.commands import command, GroupMixin
from pymongo import MongoClient

from blahaj_bot import __version__
from blahaj_bot.backlog import command_backlog
from blahaj_bot.role import command_role

logger = logging.getLogger(__name__)

class MyClient(commands.Bot):

    def __init__(self, *,
                 db: MongoClient[Mapping[str, Any]],
                 command_prefix,
                 backlog: BacklogClient,
                 intents: discord.Intents, **options: Any):
        super().__init__(command_prefix=command_prefix, intents=intents, **options)
        self.db = db
        self.backlog = backlog
        super().load_extension('cogs.basic')

    async def on_ready(self):
        logger.info(f'Logged on as {self.user}! - Version {__version__}')

    @commands.command()
    async def role(self, ctx: commands.Context, *, argv: List[str]):
        await command_role(db=self.db, ctx=ctx, argv=argv)

    @commands.command()
    async def backlog(self, ctx: commands.Context, *, argv: List[str]):
        await command_backlog(backlog=self.backlog, ctx=ctx, argv=argv)