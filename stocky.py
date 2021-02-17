#!/usr/bin/python3.6

import discord
import logging
import os

global me
me = os.path.dirname(os.path.realpath(__file__))

logging.basicConfig(handlers=[logging.FileHandler('logging.log', 'w', 'utf-8')],
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

check_rate = 10  # minutes

if __name__ == "__main__":
    logging.info('Starting discord bot')
    import bot.main
