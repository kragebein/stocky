#!/usr/bin/python3.6
import discord, asyncio, sys, datetime
from discord.ext import commands, tasks

class saythis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.set = False
        self.time = False
        self.sentence = False
        self.channel = None
        self.event = None
        self.past = False

    # Internal loop 
    @tasks.loop(seconds=60.0)
    async def outerloop(self):
        ''' Loop will be invoked once a timer is set. '''
        now = datetime.datetime.now()
        past = now.hour + now.minute
        if self.time != False:
            if past == now.hour + self.time + now.minute:
                await self.channel.send(' '.join(self.sentence))
                past = now.hour
    @outerloop.before_loop
    async def before_loop(self):
        print('[saythis] Starting secondary loop')
        await self.bot.wait_until_ready()
    @outerloop.after_loop
    async def after_loop(self):
        print('[saythis] Secondary loop stopped.')

    # Process input data.
    @commands.command(name='saythis', description='Says somethign every x hours', usage='.saythis')
    async def saythis(self, ctx):
        content = ctx.message.content
        content = content.split()
        channel = ctx.message.channel
        if content[1] == 'help':
            await ctx.send('Syntax: !saythis #channel <hours> <message>')
            await ctx.send('The bot will say <message> every <hours> in #channel')
            return
        # stop the loop
        if content[1] == 'stop':
            if self.set == False:
                await ctx.send('There isnt anything set.')
                return
            if self.set == True:
                self.set = False
                self.time = False
                self.sentence = False
                self.channel = None
                self.outerloop.cancel()
                await ctx.send('Announce was removed')
                return
        # start the loop
        time = content[1]
        message = content[2:]
        if len(content[1]) > 3: # got int longer than timestamp. Assume channel ID.
            channel = content[1].replace('<', '').replace('>','').replace('#','')
            try:
                channel = self.bot.get_channel(int(channel))
            except:
                await ctx.send('Erroneous user input') # user did something wrong.
                return
            time = content[2]
            message = content[3:]
        try:
            time = int(time)
        except:
            await ctx.send(f'Only an hour format will be accepted, you wrote "{time}"')
            return
        self.time = time
        self.sentence = message
        self.channel = channel
        message = ' '.join(self.sentence)
        a = f'Will announce "{message}" every {str(self.time)} hour(s) in {self.channel}'
        if self.set == True: # Dont kill the loop, instead change the loop params.
            await ctx.send(f'Timer changed. {a}')
        elif self.set == False:
            await ctx.send(f'Timer enabled. {a}')
            await channel.send(' '.join(self.sentence))
            self.outerloop.start()
        self.set = True
def setup(bot):
    bot.add_cog(saythis(bot))
