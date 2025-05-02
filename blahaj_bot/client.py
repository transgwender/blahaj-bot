# This example requires the 'message_content' intent.

import discord
import logging

logger = logging.getLogger(__name__)

class MyClient(discord.Client):
    async def on_ready(self):
        logger.info(f'Logged on as {self.user}!')

    async def on_message(self, message):
        logger.info(f'Message from {message.author}: {message.content}')