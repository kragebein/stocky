#!/usr/bin/python3.6

import discord
import time
import asyncio
import logging
from discord.ext import commands
from bot.extensionloader import ExtensionLoader
from bot.auth import Authenticator
from bot.tools import buildembed

# TODO: create better discord answers when things dont act as it should


class Extensions(ExtensionLoader, commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='plugin', description='Plugin controller', usage='.plugin [load|unload|reload|list|help] <extension>')
    async def plugin(self, ctx):
        content = ctx.message.content
        content = content.split()

        if len(content) == 1:
            await ctx.send(ctx.command.description)
            return

        elif len(content) >= 2:
            #
            # .plugin load [extension]
            #
            if content[1] == 'load':
                # Load one named extension.
                if len(content) >= 3:
                    loadThis = content[2]

                    if ctx.bot.get_cog(loadThis) == None:
                        self.prepareLoader(self.bot, 'load', loadThis)

                        if ctx.bot.get_cog(loadThis) == None:
                            await ctx.send('Could not load {}'.format(loadThis))
                        else:
                            await ctx.send('Loaded: {}'.format(loadThis))

                    else:
                        await ctx.send('{} already loaded'.format(loadThis))

                # Load all extensions in cogs dir
                else:
                    self.prepareLoader(self.bot, 'load', None)
                    await ctx.send('Loaded all extensions.')

            #
            # .plugin unload [extension]
            #
            if content[1] == 'unload':
                # Load one named extension.
                if len(content) >= 3:
                    loadThis = content[2]

                    if ctx.bot.get_cog(loadThis) == None:
                        await ctx.send('{} not loaded'.format(loadThis))

                    else:
                        # TODO: This file does not get unloaded, however; cant see why it doesnt.
                        # add an if=extensions.py: do not unload eitherway.
                        self.prepareLoader(self.bot, 'unload', loadThis)

                        if ctx.bot.get_cog(loadThis) == None:
                            await ctx.send('Unloaded {}'.format(loadThis))

                        else:
                            await ctx.send('Could not unload: {}'.format(loadThis))

                # Load all extensions in cogs dir
                else:
                    self.prepareLoader(self.bot, 'unload', None)
                    # sjekk om det faktisk bi unloada
                    await ctx.send('Unloaded all extensions.')

            #
            # .plugin reload [extension]
            #
            if content[1] == 'reload':
                # Reload one named extension.
                if len(content) >= 3:
                    loadThis = content[2]

                    if ctx.bot.get_cog(loadThis) == None:
                        self.prepareLoader(self.bot, 'load', loadThis)

                        if ctx.bot.get_cog(loadThis) == None:
                            await ctx.send('Could not load: {}'.format(loadThis))

                        else:
                            await ctx.send('Loaded: {}'.format(loadThis))
                    else:
                        self.prepareLoader(self.bot, 'reload', loadThis)

                        if ctx.bot.get_cog(loadThis) == None:
                            await ctx.send('Could not load {}'.format(loadThis))

                        else:
                            await ctx.send('Reloaded : {}'.format(loadThis))

                # reload all extensions in cogs dir
                else:
                    self.prepareLoader(self.bot, 'reload', None)
                    # sjekk om det faktisk bi unloada
                    await ctx.send('Reloaded all extensions.')

            #
            # .plugin help [extension]
            #
            if content[1] == 'help':
                if len(content) == 2:
                    # send help for help command
                    await ctx.send('help with thissss')
                else:
                    # send help for mentioned extension/cog
                    cog = content[2]

                    try:
                        commands = self.bot.get_cog(cog).get_commands()
                    except Exception as e:
                        await ctx.send('Could not find extension')
                        logging.warn(
                            '<user> searched for {}. Error: {}'.format(cog, e))
                        return

                    cmd_list = '{} has these commands:\n'.format(cog)

                    for cmd in commands:
                        desc = cmd.description or 'N/A'
                        usage = cmd.usage or 'N/A'
                        name = cmd.name or 'N/A'

                        cmd_list += '.{} ({}) usage: {}\n'.format(name,
                                                                  desc, usage)

                        desc = usage = name = None

                    await ctx.send(cmd_list)

            #
            # .plugin list [extension]
            #
            if content[1] == 'list':
                cogs = [c for c in self.bot.cogs.keys()]
                output = 'List of all extensions:\n'
                data = {}
                for cog in cogs:
                    try:
                        commands = self.bot.get_cog(cog).get_commands()
                    except Exception as e:
                        await ctx.send('Could not find any extensions')
                        logging.warn(
                            '<user> tried to list all extensions. Cogs list: {} Error: {}'.format(cogs, e))
                        return

                    # found extension
                    for cmd in commands:
                        usage = cmd.usage or 'N/A'
                        desc = cmd.description or 'N/A'
                        name = cmd.name or 'N/A'
                        data.update(
                            {name: 'description:\n*{}*\nusage:\n*{}*'.format(desc, usage)})
                output = buildembed(
                    'Plugins', 'This is a descriptor of loaded plugins', json_data=data)
                await ctx.send(embed=output)


def setup(bot):
    bot.add_cog(Extensions(bot))
