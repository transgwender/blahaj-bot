import logging
from typing import List

from discord import Message
from backloggery import BacklogClient

logger = logging.getLogger(__name__)

async def command_backlog(message: Message, command: List[str], backlog: BacklogClient):
        await message.channel.send('WIP')