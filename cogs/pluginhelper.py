#!/usr/bin/python3.6
import discord, asyncio, sys
from discord.ext import commands
from Levenshtein import distance as levenshtein_distance

class pluginhelper(commands.Cog):
    ''' pluginhelper helps identify erroneous commands, and suggest a possible correct command '''
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='asdasd', description='any', usage='.*')
    async def pluginhelper(self, ctx):
        print('Yes')
        plugins = ''
        trigger = 'lame' if len(sys.argv) < 2  else sys.argv[1]
        possiblematches = []
        scores = []
        accuracy = 3
        # compares string and suggest possible matches to trigger if any exists.
        for i in plugins:
            # store scores
            point = levenshtein_distance(trigger, i)
            if point <= accuracy:
                scores.append(i)
        if len(scores) == 1:
            print('Did you mean {}?'.format(scores[0]))
        elif len(scores) >= 1:
            print('Did you maybe mean {}?'.format(' or '.join(scores)))


def setup(bot):
    bot.add_cog(pluginhelper(bot))

