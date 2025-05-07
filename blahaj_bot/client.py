# This example requires the 'message_content' intent.

import discord
import logging

logger = logging.getLogger(__name__)

class MyClient(discord.Client):
    async def on_ready(self):
        logger.info(f'Logged on as {self.user}! - Version 0.0.1')

    async def on_message(self, message):
        logger.info(f'Message from {message.author}: {message.content}')

        if message.author == self.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')
        
        if message.content.startswith('$pat'):
            await message.channel.send('pat the pand')