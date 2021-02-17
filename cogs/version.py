#!/usr/bin/python3.6
import discord, asyncio, sys
from discord.ext import commands

class version(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='version', description='Shows this bot versions', usage='.version')
    async def version(self, ctx):
        pythonVersion = sys.version.split(' ')[0]
        discordpyVersion = discord.__version__
        await ctx.send('**Stocky:** v0.1, **Python:** {}, **Discordpy:** {}'.format(pythonVersion, discordpyVersion))


def setup(bot):
    bot.add_cog(version(bot))

