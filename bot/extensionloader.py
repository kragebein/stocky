#!/usr/bin/python3

import logging
import os
from stocky import me

from bot.tools import sql, Config
import sqlite3


class ExtensionLoader(Config):
    def __init__(self):
        pass

    #checkConfig('extension name', 'channel name')
    # returns True or False if the given channel is registered in the sql table or not.
    def checkConfig(self, extension, channely):
        query = 'select channels from extensions where extension = \'{}\''.format(
            extension)
        try:
            results = sql(query, 'dict')
        except Exception as e:
            print('checkConfig error: {}. Exception: {}'.format(query, e))

        if results['success']:
            if results['results']:
                channels = []

                for x in results['results']:
                    channels.append(x['channels'])

                if str(channely) in channels:
                    return True
                else:
                    return False

    # newornah('extension')
    # adds the extension to sql table if its not already there. default admin channel to #admin
    # TODO: use config file referance rather than hardcoded #admin.
    def newornah(self, file):
        query = 'select extension from extensions where extension = \'{}\''.format(
            file)
        try:
            results = sql(query, 'dict')
        except Exception as e:
            print('except: {}'.format(e))

        if results['success']:
            if not results['results']:
                logging.info('Found new extension: {}'.format(file))
                query = 'insert into extensions (extension, channels) values ("{}", "{}")'.format(
                    file, 'admin')
                try:
                    sql(query)
                    print('Found new extension: {}'.format(file))
                except Exception as e:
                    print(e)
        else:
            logging.error(
                'Error while adding new extension to SQL, with query: {}'.format(query))

    def loadExt(self, bot, file):
        try:
            if file not in bot.extensions:
                # self.newornah(file)

                logging.info('Loading extension: {}'.format(file))
                print('Loading extension: {}'.format(file))
                bot.load_extension('cogs.' + file)
            else:
                print("allerede loada" + file)
        except Exception as e:
            logging.error('Could not load extension: {}'.format(e))
            return('Error: {}'.format(e))

    def unloadExt(self, bot, file):
        try:
            if bot.get_cog(file) != None:
                logging.info('Unloading extension: {}'.format(file))
                bot.unload_extension('cogs.' + file)
            else:
                print("Not loaded " + file)
        except Exception as e:
            logging.error('Could not unload extension: {}'.format(e))
            return('Error: {}'.format(e))

    def reloadExt(self, bot, file):
        self.unloadExt(bot, file)
        self.loadExt(bot, file)

    def prepareLoader(self, bot, action, target=None):
        # bot = discord client
        # action = load/unload
        # target = None(action goes for all files in /cogs), or <file>

        cogdir = me + '/cogs'

        if action == 'load':
            if target == None:
                for f in os.listdir(cogdir):
                    if os.path.isfile(cogdir + '/' + f):
                        file = f[:-3]
                        self.loadExt(bot, file)

            else:
                if os.path.isfile(cogdir + '/' + target + '.py'):
                    return self.loadExt(bot, target)

        elif action == 'unload':
            if target == None:
                for f in os.listdir(cogdir):
                    if os.path.isfile(cogdir + '/' + f):
                        file = f[:-3]
                        self.unloadExt(bot, file)

            else:
                if os.path.isfile(cogdir + '/' + target + '.py'):
                    return self.unloadExt(bot, target)

        elif action == 'reload':
            self.prepareLoader(bot, 'unload', target)
            self.prepareLoader(bot, 'load', target)

        else:
            logging.error('Unknown action ({}) in cogloader'.format(action))
