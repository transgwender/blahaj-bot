import logging
from typing import List

from discord import Message
from pymongo import MongoClient

logger = logging.getLogger(__name__)

async def command_role(message: Message, command: List[str], db: MongoClient):
    serverdb = db[str(message.guild.id)]
    rolescol = serverdb["roles"]
    result = rolescol.replace_one({"role": "debug"}, {"role": "debug"}, upsert=True)
    logger.info(f'{message.guild.name} -- {result}')
    for x in rolescol.find():
        logger.info(f'{x}')
    await message.channel.send('WIP')