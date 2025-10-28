import json
from json import JSONEncoder

import discord
from discord import SlashCommandGroup
from discord.ext import commands

import requests
from requests import HTTPError

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

    @quotes.command(description="Add quote")
    @commands.guild_only()
    @discord.default_permissions(administrator=True)
    @discord.option("quote", description="Quote", input_type=str, required=True)
    @discord.option("person", description="Person", input_type=str)
    @discord.option("date", description="Date", input_type=str)
    async def add_quote(self, ctx: discord.ApplicationContext, quote, person="", date=""):
        quote = Quote(quote=quote, person=person, date=date)
        data = json.dumps(quote, cls=QuoteEncoder).encode('utf-8')
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': f'BlahajBot v{__version__} (dev[at]gwenkornak.ca)',
            'X-DB-Auth-Key': self.bot.quotes_auth_token
        }
        r = requests.post(f"https://api.robotcowgirl.farm/v1/quotes/{ctx.guild_id}", data=data, headers=headers)
        try:
            r.raise_for_status()
        except HTTPError as e:
            logger.error(f'Was unable to create quote {quote}: {e}')
            await ctx.respond(f'Unable to create quote', ephemeral=True)
            return
        except ConnectionError as e:
            logger.error(f'Failed to reach server: {e}')
            await ctx.respond(f'Failed to reach server', ephemeral=True)
            return
        result = r.json(object_hook=as_quote)
        quote_id = result.id
        await ctx.respond(f'Added quote #{quote_id}, {result}', ephemeral=True)

    @quotes.command(description="Edit quote")
    @commands.guild_only()
    @discord.default_permissions(administrator=True)
    @discord.option("quote_id", description="Quote ID", input_type=int, required=True)
    @discord.option("quote", description="New Quote", input_type=str, required=True)
    @discord.option("person", description="New Person", input_type=str)
    @discord.option("date", description="New Date", input_type=str)
    async def edit_quote(self, ctx: discord.ApplicationContext, quote_id, quote, person="", date=""):
        quote = Quote(quote=quote, person=person, date=date)
        data = json.dumps(quote, cls=QuoteEncoder).encode('utf-8')
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': f'BlahajBot v{__version__} (dev[at]gwenkornak.ca)',
            'X-DB-Auth-Key': self.bot.quotes_auth_token
        }
        r = requests.patch(f"https://api.robotcowgirl.farm/v1/quotes/{ctx.guild_id}/{quote_id}", data=data, headers=headers)
        try:
            r.raise_for_status()
        except HTTPError as e:
            logger.error(f'Was unable to edit quote {quote}: {e}')
            await ctx.respond(f'Unable to edit quote', ephemeral=True)
            return
        except ConnectionError as e:
            logger.error(f'Failed to reach server: {e}')
            await ctx.respond(f'Failed to reach server', ephemeral=True)
            return
        await ctx.respond(f'Edited quote #{quote_id}', ephemeral=True)

    @quotes.command(description="Delete quote")
    @commands.guild_only()
    @discord.default_permissions(administrator=True)
    @discord.option("quote_id", description="Quote ID", input_type=int, required=True)
    async def delete_quote(self, ctx: discord.ApplicationContext, quote_id):
        headers = {
            'User-Agent': f'BlahajBot v{__version__} (dev[at]gwenkornak.ca)',
            'X-DB-Auth-Key': self.bot.quotes_auth_token
        }
        r = requests.delete(f"https://api.robotcowgirl.farm/v1/quotes/{ctx.guild_id}/{quote_id}", headers=headers)
        try:
            r.raise_for_status()
        except HTTPError as e:
            logger.error(f'Was unable to delete quote {quote_id}: {e}')
            await ctx.respond(f'Unable to delete quote', ephemeral=True)
            return
        except ConnectionError as e:
            logger.error(f'Failed to reach server: {e}')
            await ctx.respond(f'Failed to reach server', ephemeral=True)
            return
        await ctx.respond(f'Deleted quote #{quote_id}', ephemeral=True)

    @quotes.command(description="Get quote")
    @commands.guild_only()
    @discord.option("quote_id", description="Quote ID", input_type=int, required=True)
    async def get_quote(self, ctx: discord.ApplicationContext, quote_id):
        headers = {
            'User-Agent': f'BlahajBot v{__version__} (dev[at]gwenkornak.ca)',
        }
        r = requests.get(f"https://api.robotcowgirl.farm/v1/quotes/{ctx.guild_id}/{quote_id}", headers=headers)
        try:
            r.raise_for_status()
        except HTTPError as e:
            logger.error(f'Failed to get quote id {quote_id}: {e}')
            await ctx.respond(f'No quote found for quote {quote_id}', ephemeral=True)
            return
        except ConnectionError as e:
            logger.error(f'Failed to reach server: {e}')
            await ctx.respond(f'Failed to reach server', ephemeral=True)
            return
        result = r.json(object_hook=as_quote)
        await ctx.respond(f'Quote #{quote_id}, {result}', ephemeral=True)

    @quotes.command(description="Get random quote")
    @commands.guild_only()
    async def get_random_quote(self, ctx: discord.ApplicationContext):
        headers = {
            'User-Agent': f'BlahajBot v{__version__} (dev[at]gwenkornak.ca)',
        }
        r = requests.get(f"https://api.robotcowgirl.farm/v1/quotes/{ctx.guild_id}/random", headers=headers)
        try:
            r.raise_for_status()
        except HTTPError as e:
            logger.error(f'Failed to get quote: {e}')
            await ctx.respond(f'No quotes found', ephemeral=True)
            return
        except ConnectionError as e:
            logger.error(f'Failed to reach server: {e}')
            await ctx.respond(f'Failed to reach server', ephemeral=True)
            return
        result = r.json(object_hook=as_quote)
        await ctx.respond(f'Quote #{result.id}, {result}', ephemeral=True)

    @quotes.command(description="Get all quotes")
    @commands.guild_only()
    async def get_quotes(self, ctx: discord.ApplicationContext):
        headers = {
            'User-Agent': f'BlahajBot v{__version__} (dev[at]gwenkornak.ca)',
        }
        r = requests.get(f"https://api.robotcowgirl.farm/v1/quotes/{ctx.guild_id}", headers=headers)
        try:
            r.raise_for_status()
        except HTTPError as e:
            logger.error(f'Failed to get quotes: {e}')
            await ctx.respond(f'No quotes found', ephemeral=True)
            return
        except ConnectionError as e:
            logger.error(f'Failed to reach server: {e}')
            await ctx.respond(f'Failed to reach server', ephemeral=True)
            return
        data = r.json()
        for quote in data:
            await ctx.respond(f'{quote}', ephemeral=True)

def setup(bot):
    bot.add_cog(Quotes(bot))