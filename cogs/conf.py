
import discord
import logging
from discord.ext import commands
from bot.tools import sql
from bot.extensionloader import ExtensionLoader


class conf(commands.Cog, ExtensionLoader):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='conf', description='Commands to configure your bot.', usage='How do you use it? idk')
    async def conf(self, ctx):
        # Only respond to configured channels. Default: #admin.
        if self.checkConfig(ctx.command.name, ctx.message.channel):
            content = ctx.message.content
            content = content.split()

            # template triggered. respond with description of plugin.
            if len(content) == 1:
                await ctx.send(ctx.command.description)
                return

            elif len(content) >= 2:
                print(content)

                #
                # .conf addchan <extension> <channel>
                #
                if content[1] == 'addchan':
                    if len(content) >= 4:
                        ext = content[2]
                        chan = content[3]

                        extCheck = 'cogs.' + ext
                        if extCheck in self.bot.extensions:
                            if chan[0] == '#':
                                chan = chan[1:]

                            if len(chan) == 0:
                                await ctx.send('Sneaky bitch')
                            else:
                                if self.checkConfig(ext, chan):
                                    await ctx.send('{} should already have access to {}.'.format(ext, chan))
                                else:
                                    logging.info(
                                        'Adding new channel ({}) to extension: {}'.format(chan, ext))
                                    query = 'insert into extensions (extension, channels) values ("{}", "{}")'.format(
                                        ext, chan)
                                    try:
                                        sql(query)
                                        await ctx.send('{} can now be triggered in #{}. Use conf "remchan <extension> <channel>" to remove.'.format(ext, chan))
                                    except Exception as e:
                                        logging.info(
                                            'Conf.py failed sql query: {}, exception: {}'.format(query, e))
                        else:
                            # Extension er ikke loada.
                            print("nah")

                # TODO: FUNKITJ! Ingen errors, men sqln kjør ikke.
                # .conf remchan <extension> <channel>
                #
                if content[1] == 'remchan':
                    if len(content) >= 4:
                        ext = content[2]
                        chan = content[3]

                        extCheck = 'cogs.' + ext
                        if extCheck in self.bot.extensions:
                            if chan[0] == '#':
                                chan = chan[1:]

                            if len(chan) == 0:
                                await ctx.send('Sneaky bitch')
                            else:
                                if not self.checkConfig(ext, chan):
                                    await ctx.send('{} dont have access to {}.'.format(ext, chan))
                                else:
                                    logging.info(
                                        'Removing channel ({}) from extension: {}'.format(chan, ext))
                                    query = 'delete from extensions where extension = "{}" and channels = "{}")'.format(
                                        ext, chan)
                                    try:
                                        t = sql(query)
                                        print(t)
                                        await ctx.send('Removed {} from {}'.format(ext, chan))
                                    except Exception as e:
                                        logging.info(
                                            'Conf.py failed sql query: {}, exception: {}'.format(query, e))
                        else:
                            # Extension er ikke loada.
                            print("nah")

                #
                # .conf listchan <extension>
                #
                if content[1] == 'listchan':
                    if len(content) >= 3:
                        ext = content[2]

                        extCheck = 'cogs.' + ext
                        if extCheck in self.bot.extensions:
                            query = 'select * from extensions where extension = "{}"'.format(
                                ext)
                            try:
                                results = sql(query, 'dict')

                                if results['success']:
                                    if results['results']:
                                        channels = []

                                        for x in results['results']:
                                            channels.append(x['channels'])

                                        channelString = ', '.join(channels)
                                        channels = ''
                                        await ctx.send('Extension {} is added to: {}'.format(ext, channelString))
                                else:
                                    await ctx.send('Extension {} not added to any channels.'.format(ext))

                            except Exception as e:
                                print(
                                    'conf.py error: {}. Exception: {}'.format(query, e))

                        else:
                            # Extension er ikke loada.
                            print("nah")


def setup(bot):
    bot.add_cog(conf(bot))
