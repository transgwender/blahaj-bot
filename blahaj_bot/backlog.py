from typing import List

from discord import Message
from backloggery import BacklogClient
from logging import Logger

async def command_backlog(message: Message, command: List[str], backlog: BacklogClient, logger: Logger):
        await message.channel.send('WIP')