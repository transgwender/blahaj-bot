import logging
from typing import List

from discord.ext.commands import Context
from pymongo import MongoClient

logger = logging.getLogger(__name__)

async def command_role(db: MongoClient, ctx: Context, argv: List[str]):
    serverdb = db[str(ctx.guild.id)]
    rolescol = serverdb["roles"]
    result = rolescol.replace_one({"role": "debug"}, {"role": "debug"}, upsert=True)
    logger.info(f'{ctx.guild.name} -- {result}')
    for x in rolescol.find():
        logger.info(f'{x}')
    await ctx.send('WIP')