#!/usr/bin/python3.6
'''asyncio scheduler for scheduling functions to run at a later time '''
import time
import asyncio
import json
import os
import sqlite3
import pickle
import base64
import inspect
import logging
from datetime import timedelta, datetime
logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)


class Scheduler():
    ''' Main Class. '''

    def __init__(self):
        self._reminder = {}
        self.path = os.path.dirname(os.path.abspath(__file__)) + '/asstets.db'
        self.db = None
        self.future = None

    async def database(self):
        # if path exists, grab the assets from the database.
        if os.path.exists(self.path):
            conn = sqlite3.connect(self.path)
            x = conn.cursor()
            data = x.execute('SELECT asset FROM assets;')
            results = data.fetchone()[0]
            backlog = []
            if data is not None:
                self._reminder = json.loads(results)
                logging.info('Loaded {} schedules'.format(len(self._reminder)))
                for timestamp in self._reminder:
                    if int(time.time()) > int(timestamp):
                        backlog.append(timestamp)
            if len(backlog) > 0:
                logging.info(
                    'Found {} schedules in a backlog. Executing them now.'.format(len(backlog)))
                for i in backlog:
                    await self.load(i)
                    pass
            self.db = True
        else:
            logging.info('Creating assets database')
            conn = sqlite3.connect(self.path)
            x = conn.cursor()
            data = x.execute(
                'CREATE TABLE IF NOT EXISTS assets ( asset BLOB );')
            x.execute('INSERT into assets ( asset )  VALUES ( 1 );')
            conn.commit()
            conn.close()
            self.db = True

    async def write(self):
        ''' updates database with new data '''
        conn = sqlite3.connect(self.path)
        x = conn.cursor()
        query = "UPDATE assets SET asset = '{}';".format(
            json.dumps(self._reminder))
        x.execute(query)
        logging.debug('Removed a schedule from the database')
        conn.commit()
        conn.close()

    async def update(self, dates=None, who=None, recurring=0, data=None, *args, **arguments):
        ''' Will append a new task to the Scheduler. returns timestamp for execution'''
        if self.db is None:  # Initialize database if it isnt yet loaded.
            await self.database()
        now = int(time.time())
        timestamp = now
        n = datetime.now()
        try:
            # time until 00:00 at this date (update('23-03-1996'))
            a = datetime(n.year, n.month, n.day, n.hour, n.minute, 0)
            b = datetime(int(dates.split(
                '-')[2]), int(dates.split('-')[1]), int(dates.split('-')[0]), 0, 0)
            timestamp += (b-a).total_seconds()
        except:
            timestamp == None
            pass
        try:
            # time until part of current day (update('13:37')) or next day if time entered is before current time.
            dateint = int(dates.split(':')[0]) + int(dates.split(':')[1])
            nint = n.hour + n.minute
            if dateint < nint:
                # If timestamp is behind, assume next day, subtract one hour.
                timestamp -= 3600
            timestamp += (timedelta(hours=24) - (n - n.replace(hour=int(dates.split(':')[0]), minute=int(
                dates.split(':')[1]), second=0, microsecond=0))).total_seconds() % (24 * 3600)
        except:
            timestamp == None
            pass
        try:
            # time until specific time at specific date  (update('23-03-1996 13:37'))
            a = datetime(n.year, n.month, n.day, n.hour, n.minute, 0)
            _date = dates.split(' ')[0]
            _time = dates.split(' ')[1]
            b = datetime(int(_date.split('-')[2]), int(_date.split('-')[1]), int(
                _date.split('-')[0]), int(_time.split(':')[0]), int(_time.split(':')[1]))
            timestamp += (b-a).total_seconds()
        except:
            timestamp == None
            pass

        if timestamp == now:
            # User did a boo-boo
            return False
            # return('Unknown Timestamp format "{}"\nValid format is 23:59, 01-01-1970 23:59 or just 01-01-1970'.format(dates))
            #raise TypeError('Unknown Timestamp format "{}"\nValid format is 23:59, 01-01-1970 23:59 or just 01-01-1970'.format(dates))
        for existing in self._reminder:
            if int(timestamp) == int(existing):
                timestamp += 1
        self._reminder[int(timestamp)] = {
            'who': who, 'recurring': recurring, 'data': data, 'args': args, 'arguments': arguments}
        conn = sqlite3.connect(self.path)
        x = conn.cursor()
        try:
            query = "UPDATE assets SET asset = '{}';".format(
                json.dumps(self._reminder))
            x.execute(query)
            logging.info('Wrote text schedule to sql')
            conn.commit()
        except TypeError:
            # object found, convert to base64 and decode in ascii so we can dump it in sql
            self._reminder[int(timestamp)] = {'who': who, 'recurring': recurring, 'data': base64.encodebytes(
                pickle.dumps(data)).decode('ascii'), 'args': args, 'arguments': arguments}
            query = "UPDATE assets SET asset = '{}';".format(
                json.dumps(self._reminder))
            x.execute(query)
            logging.info('Wrote object schedule to sql')
            conn.commit()
        conn.close()
        return True

    async def check(self):
        '''Check is the loop that checks if time is equal to anything in the reminder array '''
        logging.info('Scheduler started.')
        while True:
            now = int(time.time())
            if now in self._reminder:
                await self.load(now)
            # sleep to allow cpu to breathe
            await asyncio.sleep(0.2)

    async def main(self):
        ''' Start Schedule loop '''
        if self.db is None:
            await self.database()
        await self.check()

    async def load(self, asset):
        ''' loads the Scheduled data and executes it.'''
        _data = self._reminder[asset]
        who = self._reminder[asset]['who']
        recurring = self._reminder[asset]['recurring']
        data = self._reminder[asset]['data']
        arguments = self._reminder[asset]['arguments']
        args = self._reminder[asset]['args']
        if recurring == 0:
            _recurring = ''
        else:
            _recurring = 'a recurring '

        try:
            base64_bytes = data.encode('ascii')
            data = base64.b64decode(base64_bytes)
        except:
            pass

        if isinstance(data, bytes):
            _type = 'object'
            data = pickle.loads(data)
        elif isinstance(data, str):
            _type = 'text'
        if recurring == 0:
            del self._reminder[asset]
            await self.write()
        logging.debug('Running {}{} reminder for {}.\n'.format(
            _recurring, _type, who))

        # Run the function in all its glory.
        if _type == 'object':
            if arguments is None or len(arguments) is 0:
                if inspect.iscoroutinefunction(data):
                    await data()
                else:
                    data()
            else:
                if inspect.iscoroutinefunction(data):
                    await data(*args, **arguments)
                else:
                    data(*args, **arguments)
        elif _type == 'text':
            print(data)
        return True


# To start loop:
# async def test(loop):
#    from scheduler import Scheduler
#    x = Scheduler()
#    loop.create_task(x.main())
# to update scheduler with new task:
#     await x.update('18:18', who='testing123', data=function, some=argument for=the, function=you, want=arguments_for)

# To repeat the function, you can add it recursively:

# async def recursive(loop):
#    from scheduler import Scheduler
#    x = Scheduler()
#    await x.update('18:18', who='Repeat', data=recursive, loop=loop)
#    await x.update('18:18', who='Some user' data=otherfunction, argument_for_that_function='blah')
