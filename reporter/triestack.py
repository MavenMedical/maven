from reporter.timedtrie import TimedTrie
import datetime
from math import ceil


class TrieStack:

    def __init__(self, start, increment, depth):
        now = datetime.datetime.now()
        self.change = start + increment * ceil((now - start) / increment)
        self.stack = [(self.change - i * increment, TimedTrie()) for i in range(depth)]
        self.increment = increment

    def insert(self, path):
        now = datetime.datetime.now()
        while now > self.change:
            self.change += self.increment
            self.stack.pop()
            self.stack.insert(0, (self.change, TimedTrie()))

        self.stack[0][1].insert(path)

    def stats(self, path):
        return [{'stoptime': elem[0].timestamp(), 'self': elem[1].find(path).count,
                 'children': elem[1].getchildrenandcounts(path)}
                for elem in self.stack]


def test():
    ts = TrieStack(datetime.datetime.now(), datetime.timedelta(seconds=10000), 1)
    while True:
        s = input('what to insert or query? ')
        if s[0] == 'i':
            ts.insert(s[2:])
        else:
            print(ts.stats(s[2:]))
