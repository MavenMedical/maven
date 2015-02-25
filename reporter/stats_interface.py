import asyncio
from reporter.triestack import TrieStack
from datetime import datetime, timedelta
from collections import defaultdict
from maven_logging import _message_to_slack


class StatsInterface:
    def __init__(self):
        self.heartbeats = defaultdict(list)
        today = datetime.today()
        self.minutestack = TrieStack(today, timedelta(minutes=1), 5)
        self.hourstack = TrieStack(today, timedelta(hours=1), 5)
        self.daystack = TrieStack(today, timedelta(days=1), 7)
        asyncio.async(self.monitor_heartbeats(10))
        print('starting stats interface')

    @asyncio.coroutine
    def monitor_heartbeats(self, interval):
        while True:
            now = datetime.now()
            try:
                for name, last_ten in list(self.heartbeats.items()):
                    if len(last_ten) < 10:
                        continue
                    span = now - last_ten[0]
                    if last_ten[-1] < now - span / 2:
                        yield from _message_to_slack(name + ' has stopped posting heartbeats')
                        self.heartbeats.pop(name)
                yield from asyncio.sleep(interval)
            except Exception as e:
                print(e)

    @asyncio.coroutine
    def insert(self, path):
        self.minutestack.insert(path)
        self.hourstack.insert(path)
        self.daystack.insert(path)
        if path.endswith('/heartbeat'):
            heartbeats = self.heartbeats[path]
            heartbeats.append(datetime.now())
            if len(heartbeats) > 10:
                heartbeats.pop(0)
            # print([x.second for x in heartbeats])

    @asyncio.coroutine
    def minutestats(self, path):
        return self.minutestack.stats(path)

    @asyncio.coroutine
    def hourstats(self, path):
        return self.hourstack.stats(path)

    @asyncio.coroutine
    def daystats(self, path):
        return self.daystack.stats(path)
