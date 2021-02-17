#!/usr/bin/python3

import os
import logging
import discord
import json
import time
from discord import Webhook, RequestsWebhookAdapter
from discord.ext import commands
from stocky import me
from bot.tools import Config, adduser, buildembed, User
from bot.extensionloader import ExtensionLoader
import discord
global bot

webhooks = []
conf = Config()


def get_prefix(bot, message):
    prefixes = json.loads(conf.trigger)
    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)


bot = commands.Bot(command_prefix=get_prefix, description='desc')
# remove default help command
bot.remove_command('help')

# Load all extensions
x = ExtensionLoader()
x.prepareLoader(bot, 'load')


async def say(text=None, embed=None, where=None):
    ''' adapter for saying stuff, will use existing webhooks or create if needed '''
    WEBHOOK_ID = ''
    WEBHOOK_TOKEN = ''
    # look up already existing webhooks that is set up for the bot.
    for w in range(0, len(webhooks)):
        obj = webhooks[w]
        if obj.name == bot.user.display_name and obj.channel.id == where:
            WEBHOOK_ID = obj.id
            WEBHOOK_TOKEN = obj.token
    else:  # if the webhook is nonexistant, create it.
        try:
            chan = discord.utils.get(
                bot.get_all_channels(), guild__name='Stocky', id=int(where))
            wb = await chan.create_webhook(name=bot.user.display_name)
            webhooks.append(wb)
            WEBHOOK_ID = wb.id
            WEBHOOK_TOKEN = wb.token
            logging.debug(
                'Webhook created for textchannel "{}"'.format(wb.channel))
        except:
            logging.warn(
                'Does the bot have "manage_webhooks" flag? Couldnt create webhooks for {}'.format(where))
            return
    webhook = Webhook.partial(
        WEBHOOK_ID, WEBHOOK_TOKEN, adapter=RequestsWebhookAdapter())
    webhook.send(text, embed=embed, username=bot.user.display_name)


def on_command_error(ctx, error):

    send_help = (commands.MissingRequiredArgument, commands.BadArgument, commands.TooManyArguments, commands.UserInputError)

    if isinstance(error, commands.CommandNotFound):  # fails silently
        print('We captured the error')


@bot.event
async def on_ready():
    logging.info('Connected discord as {}'.format(bot.user.name))
    print(f'{bot.user.name} has connected to Discord!')
    print(f'discord version {discord.__version__}')
    for guild in bot.guilds:
        guild_id = guild.id
        for member in guild.members:
            channels = []
            memberdata = await bot.fetch_user(member.id)
            name = memberdata.display_name
            if memberdata != bot.user:  # Dont add self.
                author = member.id
                avatar = memberdata.avatar_url
                is_bot = memberdata.bot
                mention = memberdata.mention
                common_name = name.split('#')[0]
                for channel in guild.channels:
                    channel_id = channel.id
                    channels.append(channel_id)
                adduser(username=name, guild_id=guild_id, user_id=author, common_name=common_name,
                        channels=channels, avatar=avatar, is_bot=is_bot, mentionstring=mention)
                del channels
            # crate a list of webhooks with the same name as the bot.
            data = await guild.webhooks()
            for w in range(0, len(data)):
                obj = data[w]
                if obj.name == bot.user.display_name:
                    webhooks.append(obj)


# Only react to events if config has been set to 1, otherwise shut the fuck up.
if conf.react_events == 1:
    @bot.event
    async def on_message(message):
        if bot.user == message.author:
            return

    async def on_message_edit(before, after):
        await say(text='The message {} was edited to {} by {}'.format(before.content, after.content, after.user.name))

    @bot.event
    async def on_guild_channel_create(channel):
        if isinstance(channel, discord.TextChannel):
            await say(text='Text Channel Created: {}'.format(channel.name))
        elif isinstance(channel, discord.VoiceChannel):
            await say(text='Voice Channel Created: {}'.format(channel.name))

        if channel.name == 'fuck':
            await channel.delete(reason='Not allowed to create channel with this name.')
            await say(text='Channel {} was deleted due to a bad word'.format(channel.name))

    @bot.event
    async def on_guild_channel_delete(channel):
        if isinstance(channel, discord.TextChannel):
            await say(text='Text Channel deleted: {}'.format(channel.name))
        elif isinstance(channel, discord.VoiceChannel):
            await say(text='Voice Channel deleted: {}'.format(channel.name))


    @bot.event
    async def on_private_channel_create(channel):
        if isinstance(channel, discord.TextChannel):
            await say(text='Text (private) Channel created: {}'.format(channel.name))
        elif isinstance(channel, discord.VoiceChannel):
            await say(text='Voice (private) Channel created: {}'.format(channel.name))


    @bot.event
    async def on_private_Channel_delete(channel):
        if isinstance(channel, discord.TextChannel):
            await say(text='Text (private) Channel deleted: {}'.format(channel.name))
        elif isinstance(channel, discord.VoiceChannel):
            await say(text='Voice (private) Channel deleted: {}'.format(channel.name))


    @bot.event
    async def on_guild_channel_update(before, after):
        if before.name != after.name:
            await say(text='Channel {} has changed name, is now called {}'.format(before.name, after.name))


    @bot.event
    async def on_private_channel_update(before, after):
        if before.name != after.name:
            await say(text='The private channel {} has changed name, is now called {}'.format(before.name, after.name))


    @bot.event
    async def on_typing(channel, user, when):
        pass


    @bot.event
    async def on_reaction_add(reaction, user):
        await say(text='{} reacted to {} in {}.'.format(user.name, reaction.message.content, reaction.message.channel))
        await reaction.remove(user)


    @bot.event
    async def on_reaction_remove(reaction, user):
        await say(text='{} removed the reaction from {} by {} in {}'.format(user.name, reaction.message.content, reaction.message.author.name, reaction.message.channel))


    @bot.event
    async def on_guild_role_created(role):
        ''' bot must have permissions to see the roles for this to work '''
        await say(text='A new role was created: {} with the permissions: {}'.format(role.name, role.permissions))


    @bot.event
    async def on_guild_role_deleted(role):
        ''' bot must have permissions to see the roles for this to work '''
        await say(text='A role was deleted')


    @bot.event
    async def on_message_delete(message):
        await say(text='A message written by {} in {} was deleted. Message content: {}'.format(message.author, message.channel, message.content))


    @bot.event
    async def on_guild_join(guild):
        await say(text='Joined a new guild! Guild name: {}, guild id: {}'.format(guild.name, guild.id))


    @bot.event
    async def on_guild_remove(guild):
        await say(text='Left a the {} ({}) Guild.'.format(guild.id, guild.name))


    @bot.event
    async def on_user_update(before, after):
        pass


    @bot.event
    async def on_voice_state_update(member, before, after):
        user = User()
        data = {}
        data.update({'thumbnail': user.avatar(member.guild.id, member.id)})
        if after.channel == None:
            state = 'left the voice chat {}'.format(before.channel)
        elif before.channel != None:
            state = 'changed from {} channel to the {}'.format(
                before.channel, after.channel)
        else:
            state = 'joined the voice chat {}'.format(after.channel)
        if after.channel != None:
            afk = 'yes' if after.afk == True else 'no'
            self_mute = 'yes' if after.self_mute == True else 'no'
            self_deaf = 'yes' if after.self_deaf == True else 'no'
            self_video = 'yes' if after.self_video == True else 'no'
            server_mute = 'yes' if after.mute == True else 'no'
            data.update({'is afk?': afk})
            data.update({'is locally muted?': self_mute})
            data.update({'is locally deafend?': self_deaf})
            data.update({'is broadcasting?': self_video})
            data.update({'is muted on server?': server_mute})

        embed = buildembed('Voice chat update!', member.name +
                        ' ' + state, json_data=data)
        await say(text='', embed=embed)


    @bot.event
    async def on_resumed():
        ''' ronny, her burde du sjekk helsa på alle cogs '''
        pass


    @bot.event
    async def on_invite_create(invite):
        #invite_url = invite.url
        channel = invite.channel
        guild = invite.guild
        inviter = invite.inviter
        # Check if user is allowed to invite. here
        await say(text='An invite was created to the channel #{} in {} by {}'.format(channel, guild.name, inviter))
        await invite.delete()


    @bot.event
    async def on_invite_delete(invite):
        await say(f'Invite url to #{invite.channel} {invite.url} was deleted.')


    @bot.event
    async def on_guild_role_create(role):
        await say(text=f'A new role, {role.name}, was created in {role.guild}')
        pass


    @bot.event
    async def on_guild_role_delete(role):
        await say(text=f'The role {role.name} in {role.guild} was deleted.')
        pass


    @bot.event
    async def on_guild_role_update(before, after):
        ''' Very much to unpack on this trigger, needs a whole damn lot work '''
        changes = ''
        if before.name != after.name:
            changes += 'Name was changed from "{}" to "{}\n"'.format(
                before.name, after.name)
        if before.color != after.color:
            changes += 'Color was changed from "{} to "{}\n'.format(
                before.color, after.color)
        before_members = []
        after_members = []
        for i in before.members:
            before_members.append(i.name)
        for i in after.members:
            after_members.append(i.name)
        be = set(before_members).difference(after_members)
        if len(be) != 0:
            af = set(after_members).intersection(before_members)
            removed = []
            added = []
            for k in af:
                if k not in before_members:
                    removed.append(k)
            for a in af:
                if a in after_members:
                    added.append(a)
            changes += 'Amount of role members have changed.\n - Added: {}\n - Removed: {}'.format(
                added, removed)

        await say(text=f'A role in {before.guild} was edited.\n{changes} ')
        pass


    @bot.event
    async def on_member_join(member):
        await say(text='{} has become a member! Hooray!'.format(member.name))
        # adduser(username=member.name, guild_id=member.guild.id, user_id=member.id, common_name=str(member.name).split("#")[0], channels=member.channels, avatar=avatar, is_bot=is_bot, mentionstring=mention)


    @bot.event
    async def on_member_remove(member):
        await say(text='{} has been removed from the guild.'.format(member.name))


    @bot.event
    async def on_member_update(before, after):
        if before.id == bot.user.id:  # Don't really want to update on ourself.
            return
        from bot.tools import User, buildembed
        user = User()
        fields = {}
        if before.display_name != after.display_name:
            fields['namechange'] = after.display_name
        if before.color != after.color:
            fields['colorchange'] = after.color
        embed = buildembed('A member was updated', 'Some changes were discovered',
                        colorchange=after.color, thumbnail=user.avatar(before.guild.id, before.id))
        # await say(embed=embed)

    #discord.on_member_update(before, after)
    #discord.on_user_update(before, after)
    # discord.on_guild_join(guild)
    # discord.on_guild_remove(guild)
    #discord.on_guild_update(before, after)
    # discord.on_guild_available(guild)
    # discord.on_guild_unavailable(guild)
    #discord.on_voice_state_update(member, before, after)
    #discord.on_member_ban(guild, user)
    #discord.on_member_unban(guild, user)
    #discord.on_group_join(channel, user)
    #discord.on_group_remove(channel, user)
    # discord.on_relationship_add(relationship)
    # discord.on_relationship_remove(relationship)
    #discord.on_relationship_update(before, after)
    # discord.on_bulk_message_delete(messages)
    # discord.on_raw_bulk_message_delete(payload)
    #discord.on_private_channel_update(before, after)
    #discord.on_private_channel_pins_update(channel, last_pin)
    #discord.on_guild_channel_pins_update(channel, last_pin)
    # discord.on_guild_integrations_update(guild)
    # discord.on_webhooks_update(channel)

bot.run(conf.token, bot=True, reconnect=True)
