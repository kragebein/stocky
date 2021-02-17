#!/usr/bin/python3

import logging, os
from stocky import me

# Authenticator.check(client, nickname, channel, trigger)
# This will run on each cogs/ __init__. If the user does not have permission to do the action in the channel; return False.
# Needs to be imported in every plugin that want restricted accessability.

class Authenticator():
    # check if configurations are available.
    def __init__(self):
        pass

    # run on every __init__ on plugins.
    async def check(self,bot,user=None,channel=None,action=None):
        pass

    # triggered by extension: edit priveliges to user.
    async def edit(self,bot,user=None,channel=None,action=None):
        pass

    # triggered by extension: remove all priveliges to user.
    async def remove(self,bot,user=None,channel=None,action=None):
        pass