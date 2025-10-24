import json
from json import JSONEncoder
from urllib.error import URLError, HTTPError

import discord
from discord import slash_command, SlashCommandGroup
from discord.ext import commands
from urllib import request

from blahaj_bot import BotClient, logger, __version__

class Quote:
    quote: str
    person: str
    date: str
    id: int

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        full_quote = self.quote
        if self.person:
            full_quote += f" - {self.person}"
        if self.date:
            full_quote += f", {self.date}"
        return full_quote

class QuoteEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

def as_quote(dct: dict):
    if 'quote' not in dct:
        return None
    return Quote(**dct)

class Quotes(commands.Cog):

    def __init__(self, bot: BotClient):
        self.bot = bot

    quotes = SlashCommandGroup("quotes", "Commands for getting quotes")

    @quotes.command(description="Add quote to database", guild_only=True)
    @discord.default_permissions(administrator=True)
    @discord.option("quote", description="Quote", input_type=str, required=True)
    @discord.option("person", description="Person", input_type=str, required=True)
    @discord.option("date", description="Date", input_type=str, required=True)
    async def add_quote(self, ctx: discord.ApplicationContext, quote, person, date):
        quote = Quote(quote=quote, person=person, date=date)
        data = json.dumps(quote, cls=QuoteEncoder).encode('utf-8')
        req = request.Request(f"https://api.robotcowgirl.farm/v1/quotes/{ctx.guild_id}")
        req.add_header('Content-Type', 'application/json')
        req.add_header('User-Agent', f'Blahaj-Bot/{__version__} (dev[at]gwenkornak.ca)')
        req.add_header('X-DB-Auth-Key', self.bot.quotes_auth_token)
        try:
            resp = request.urlopen(req, data)
        except HTTPError as e:
            logger.error(f'Was unable to create quote {quote}: {e}')
            await ctx.respond(f'Unable to create quote', ephemeral=True)
            return
        except URLError as e:
            logger.error(f'Failed to reach server: {e}')
            await ctx.respond(f'Failed to reach server', ephemeral=True)
            return
        result = json.loads(resp.read().decode('utf-8'), object_hook=as_quote)
        quote_id = result.id
        await ctx.respond(f'Added quote {quote_id}, {result}', ephemeral=True)

    @quotes.command(description="Get quote from database", guild_only=True)
    @discord.option("quote_id", description="Quote ID", input_type=int, required=True)
    async def get_quote(self, ctx: discord.ApplicationContext, quote_id):
        req = request.Request(f"https://api.robotcowgirl.farm/v1/quotes/{ctx.guild_id}/{quote_id}")
        req.add_header('User-Agent', f'Blahaj-Bot/{__version__} (dev[at]gwenkornak.ca)')
        try:
            resp = request.urlopen(req)
        except HTTPError as e:
            logger.error(f'Failed to get quote id {quote_id}: {e}')
            await ctx.respond(f'No quote found for quote {quote_id}', ephemeral=True)
            return
        except URLError as e:
            logger.error(f'Failed to reach server: {e}')
            await ctx.respond(f'Failed to reach server', ephemeral=True)
            return
        quote = json.loads(resp.read().decode('utf-8'), object_hook=as_quote)
        await ctx.respond(f'Quote {quote_id}, {quote}', ephemeral=True)

def setup(bot):
    bot.add_cog(Quotes(bot))