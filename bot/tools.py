#!/usr/bin/python3.6
''' Contains various tools '''
import os
import sqlite3
import logging
import configparser
import discord
import json
import datetime
import time
# def useradd(username=None, guild=None, userid=None, channels=None,
# user_rank=0):#


#       from stocky import me
# TODO: ^ does not work when tools.py is imported from same directory.
# create function.
global me
me = os.path.dirname(os.path.realpath(__file__))


def sql(data, format=dict):
    ''' Sql is an easy way to connect to the db by just doing queries directly
        data = sql('select * from extensions)
        use format=tuple/dict
    '''
    try:
        import sqlite3
    except ImportError:
        raise('cannot use sqlite3. Update to Python 3.6')
    if not os.path.exists('database.db'):
        conn = sqlite3.connect('database.db')
        y = conn.cursor()
        query = [
            "CREATE TABLE users (ID INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, guild_id INT, user_id INT, user_rank INT, common_name TEXT, channels TEXT, avatar TEXT, is_bot TEXT, mentionstring TEXT)",
            "CREATE TABLE settings (discord_token TEXT, superadmin INT)",
            "CREATE TABLE extensions (ID INTEGER PRIMARY KEY AUTOINCREMENT, extension TEXT, channels TEXT)"]
        for z in query:
            y.execute(z)
            conn.commit()
        y.close()
    _exception = False
    conn = sqlite3.connect('database.db')

    conn.row_factory = sqlite3.Row
    y = conn.cursor()
    try:
        results = y.execute(data)
    except Exception as R:
        _exception = R
        pass
    try:
        conn.commit()
    except Exception:
        pass
    if format == 'dict':
        if _exception:
            result = {'results': None, 'success': False, 'error': _exception}
            return result
        result = {
            'results': [
                dict(row) for row in results.fetchone()],
            'success': True}
        return result
    elif format == 'tuple':
        return results.fetchall()


def adduser(
        username=None,
        guild_id=None,
        user_id=None,
        user_rank=0,
        common_name=None,
        channels=None,
        avatar=None,
        is_bot=None,
        mentionstring=None):
    ''' Adds a user to the database '''
    # we can increase the user resolution by adding and channels = "{}" in the
    # check query
    check = sql(
        'SELECT ID FROM users WHERE user_id = "{}" and guild_id = "{}"'.format(
            user_id,
            guild_id),
        format='tuple')
    if len(check) == 0:  # Check if this user is registered on this guild, if so - ignore
        try:
            query = 'INSERT into users (username, guild_id, user_id, user_rank, common_name, channels, avatar, is_bot, mentionstring) VALUES("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(
                username, guild_id, user_id, user_rank, common_name, channels, avatar, is_bot, mentionstring)
            sql(query, format='tuple')
            print('Adding user..{}'.format(username))
            logging.debug(
                'Added new user, {}, from guild {} to known users.'.format(
                    user_id, guild_id))
        except Exception as R:
            logging.debug('Unable to add user, error from query: {}'.format(R))


class Config():
    def __init__(self):
        self.file = 'config.ini'
        self.config = configparser.ConfigParser()
        if not os.path.exists(self.file):
            print('{} not found, creating default config..'.format(self.file))
            self.config['STOCKY'] = {
                'discord_token': 'None', 'username': 'None'}
            self.config['BOT'] = {
                'trigger_prefix': '[".","!","@","?"]',
                'check_plugins': 'True',
                'check_updates': 'True',
                'react_events': 0}
            with open(self.file, 'w') as configfile:
                try:
                    self.config.write(configfile)
                    logging.info('Created new configuration')
                except Exception as R:
                    logging.debug(
                        'Unable to create configuration!: {}'.format(R))
                    raise Exception(
                        'Unable to create configuration. You must ensure that you have read/write permissions')

        self.config.read(self.file)
        app = self.config['STOCKY']
        bot = self.config['BOT']
        self.token = app['discord_token']
        self.username = app['username']
        self.trigger = bot['trigger_prefix']
        self.plugincheck = bot['check_plugins']
        self.updatecheck = bot['check_updates']
        self.react_events = bot['react_events']

        # Need some error handling
        if self.token == 'None':
            raise SyntaxError(
                'Discord token is not present in the configuration file. Please update {}'.format(
                    self.file))
        if self.username == 'None':
            raise SyntaxError(
                'Bot username is not present in the configuration file. Please update {}'.format(
                    self.file))


class User():
    '''Get a user attribute from database '''

    def __init__(self, guild=None):
        # Can probably pass the server guild here if we want.
        self.guild = guild

    def level(self, guild, userid):
        ''' return auth level for user.
            Returns None if user doesnt exist, or query fails. '''
        try:
            returndata = sql(
                "SELECT user_rank FROM users WHERE guild_id = '{}' AND user_id = '{}'".format(
                    guild, userid), format='tuple')
            # Return first match, first row. [1][4] = second match, 5 row.
            return int(returndata[0][0])
        except BaseException:
            return None

    def avatar(self, guild, userid):
        ''' Returns the avatar url for this user in this guild. '''
        try:
            returndata = sql(
                "SELECT avatar FROM users WHERE guild_id = '{}' AND user_id = '{}'".format(
                    guild, userid), format='tuple')
            # Return first match, first row. [1][4] = second match, 5 row.
            return str(returndata[0][0])
        except BaseException:
            return None

    def channels(self, guild, userid):
        '''' returns a list of channels on the guild this user is member of'''
        try:
            returndata = sql(
                "SELECT channels FROM users WHERE guild_id = '{}' AND user_id = '{}'".format(
                    guild, userid), format='tuple')
            # Return first match, first row. [1][4] = second match, 5 row.
            return returndata[0][0]
        except BaseException:
            return None

    def userid(self, guild, username):
        ''' Returns the userid of the user with this username on this guild'''
        try:
            returndata = sql(
                "SELECT user_id FROM users WHERE guild_id = '{}' AND username = '{}'".format(
                    guild, username), format='tuple')
            # Return first match, first row. [1][4] = second match, 5 row.
            return int(returndata[0][0])
        except BaseException:
            return None

    def mentionstring(self, guild, userid):
        ''' returns a string that can be used to mention this user '''
        try:
            returndata = sql(
                "SELECT mentionstring FROM users WHERE guild_id = '{}' AND user_id = '{}'".format(
                    guild, userid), format='tuple')
            # Return first match, first row. [1][4] = second match, 5 row.
            return str(returndata[0][0])
        except BaseException:
            return None


def buildembed(
        title,
        description,
        url=None,
        timestamp=None,
        json_data=None,
        **argv):
    ''' Easy Embed Builder.
  ---
  Minimum requirements:
  title, description.
  Accepts both dict and name=value entries for the optional parameters
  ---
  Optional:
  url (for title), thumbnail (url), photo_url, author, footer (dict with length: 1) and timestamp
  timestamp is epoch. Will use current time if not specified.
  footer={'footer-text': 'http://www.com/image.png'}
  use json_data to programatically add fields.
  --- Discord Limits:
* Embed titles are limited to 256 characters
* Embed descriptions are limited to 2048 characters
* There can be up to 25 fields
* A field's name is limited to 256 characters and its value to 1024 characters
* The footer text is limited to 2048 characters
* The author name is limited to 256 characters
* In addition, the sum of all characters in an embed structure must not exceed 6000 characters
'''
    colors = {
        'DEFAULT': 0x000000,
        'WHITE': 0xFFFFFF,
        'AQUA': 0x1ABC9C,
        'GREEN': 0x2ECC71,
        'BLUE': 0x3498DB,
        'PURPLE': 0x9B59B6,
        'LUMINOUS_VIVID_PINK': 0xE91E63,
        'GOLD': 0xF1C40F,
        'ORANGE': 0xE67E22,
        'RED': 0xE74C3C,
        'GREY': 0x95A5A6,
        'NAVY': 0x34495E,
        'DARK_AQUA': 0x11806A,
        'DARK_GREEN': 0x1F8B4C,
        'DARK_BLUE': 0x206694,
        'DARK_PURPLE': 0x71368A,
        'DARK_VIVID_PINK': 0xAD1457,
        'DARK_GOLD': 0xC27C0E,
        'DARK_ORANGE': 0xA84300,
        'DARK_RED': 0x992D22,
        'DARK_GREY': 0x979C9F,
        'DARKER_GREY': 0x7F8C8D,
        'LIGHT_GREY': 0xBCC0C0,
        'DARK_NAVY': 0x2C3E50,
        'BLURPLE': 0x7289DA,
        'GREYPLE': 0x99AAB5,
        'DARK_BUT_NOT_BLACK': 0x2C2F33,
        'NOT_QUITE_BLACK': 0x23272A
    }
    authorlength = 256
    fieldlength = 256
    maxfields = 25
    maxchar = 6000
    namelength = 1048
    valuelength = 2048
    desclength = 2048
    # Check globals
    if json_data is not None:
        argv = json_data
    if len(title) > fieldlength:
        logging.info('Title length exceeded in embed builder.')
        print('title length')
        return None
    if len(description) > desclength:
        logging.info('Maximum description lengt exceeded in embed builder.')
        print('desc length')
        return None
    if timestamp is None:
        timestamp = int(time.time())
    embed = discord.Embed(
        title=title,
        description=description,
        url=url,
        timestamp=datetime.datetime.utcfromtimestamp(timestamp),
        colour=discord.Colour(
            colors['DARK_RED']))
    if len(argv) == 0:
        print('no data')
        logging.info('No data provided to embed builder.')
        return None
    if len(argv) > maxfields:
        print('field limit exeeded')
        logging.info('Field limit exeeded in embed builder.')
        return None
    for item in argv:
        if len(item) > namelength:
            break
        if len(str(argv[item])) > valuelength:
            break
        if item == 'footer':
            for data in argv[item]:
                embed.set_footer(text=data, icon_url=argv[item][data])
        elif item == 'author':
            if len(argv[item]) > authorlength:
                break
            else:
                embed.set_author(name=argv[item])
        elif item == 'thumbnail':
            embed.set_thumbnail(url=argv[item])
        elif item == 'photo_url':
            embed.set_image(url=argv[item])
        else:
            embed.add_field(name=item, value=argv[item])
    return embed
