import asyncio
from reporter.triestack import TrieStack
from datetime import datetime, timedelta


class StatsInterface:
    def __init__(self):
        today = datetime.today()
        self.minutestack = TrieStack(today, timedelta(minutes=1), 10)
        self.hourstack = TrieStack(today, timedelta(hours=1), 10)
        self.daystack = TrieStack(today, timedelta(days=1), 7)

    @asyncio.coroutine
    def insert(self, path):
        self.minutestack.insert(path)
        self.hourstack.insert(path)
        self.daystack.insert(path)

    @asyncio.coroutine
    def minutestats(self, path):
        return self.minutestack.stats(path)

    @asyncio.coroutine
    def hourstats(self, path):
        return self.minutestack.stats(path)

    @asyncio.coroutine
    def daystats(self, path):
        return self.minutestack.stats(path)
