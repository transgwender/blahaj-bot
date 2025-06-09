import logging

from discord.ext import commands

from blahaj_bot import BotClient

logger = logging.getLogger(__name__)

class Roles(commands.Cog):

    def __init__(self, bot: BotClient):
        self.bot = bot

    @commands.command()
    async def role(self, ctx: commands.Context):
        serverdb = self.bot.db[str(ctx.guild.id)]
        rolescol = serverdb["roles"]
        result = rolescol.replace_one({"role": "debug"}, {"role": "debug"}, upsert=True)
        logger.info(f'{ctx.guild.name} -- {result}')
        for x in rolescol.find():
            logger.info(f'{x}')
        await ctx.send('WIP')

def setup(bot):
    bot.add_cog(Roles(bot)) # add the cog to the bot