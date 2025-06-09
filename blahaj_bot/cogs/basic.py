import discord
from discord.ext import commands

from blahaj_bot import __version__

class Basic(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx: commands.Context):
        await ctx.send('Hello!')

    @commands.command()
    async def pat(self, ctx: commands.Context):
        await ctx.send('pat the pand')

    @commands.command()
    async def github(self, ctx: commands.Context):
        await ctx.send('Check out my source code at: https://github.com/transgwender/blahaj-bot')

    @commands.command()
    async def version(self, ctx: commands.Context):
        await ctx.send(f'Version {__version__}')

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Basic(bot)) # add the cog to the bot