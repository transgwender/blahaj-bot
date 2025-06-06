# This example requires the 'message_content' intent.

import discord


class MyClient(discord.Client):

    def bot_init(self, version, logger, db):
        self.version = version
        self.logger = logger
        self.db = db

    async def on_ready(self):
        self.logger.info(f'Logged on as {self.user}! - Version {self.version}')

    async def on_message(self, message):
        self.logger.info(f'Message from {message.author}: {message.content}')

        if message.author == self.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')
        
        if message.content.startswith('$pat'):
            await message.channel.send('pat the pand')

        if message.content.startswith('$github'):
            await message.channel.send('Check out my source code at: https://github.com/transgwender/blahaj-bot')

        if message.content.startswith('$version'):
            await message.channel.send(f'Version {self.version}')

        if message.content.startswith('$role'):
            serverdb = self.db[str(message.guild.id)]
            rolescol = serverdb["roles"]
            result = rolescol.replace_one({"role" : "debug"}, { "role": "debug" }, upsert = True)
            self.logger.info(f'{message.guild.name} -- {result}')
            for x in rolescol.find():
                self.logger.info(f'{x}')
            await message.channel.send('WIP')