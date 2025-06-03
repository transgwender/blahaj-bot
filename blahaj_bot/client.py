# This example requires the 'message_content' intent.

import discord
import logging

logger = logging.getLogger(__name__)
version = "0.0.2"

class MyClient(discord.Client):
    async def on_ready(self):
        logger.info(f'Logged on as {self.user}! - Version {version}')

    async def on_message(self, message):
        logger.info(f'Message from {message.author}: {message.content}')

        if message.author == self.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')
        
        if message.content.startswith('$pat'):
            await message.channel.send('pat the pand')

        if message.content.startswith('$github'):
            await message.channel.send('Check out my source code at: https://github.com/transgwender/blahaj-bot')

        if message.content.startswith('$version'):
            await message.channel.send(f'Version {version}')