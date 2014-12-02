from collections import defaultdict
from datetime import datetime


class TimedTrie:
    def __init__(self):
        self.count = 0
        self.children = defaultdict(TimedTrie)
        self.events = list()
        self.first = datetime.max
        self.last = datetime.min

    @classmethod
    def _splitpath(self, path):
        if type(path) is str:
            path = list(filter(lambda x: x, path.split('/')))
        return path

    def insert(self, path, eventtime=None):
        path = self._splitpath(path)
        # print(path)
        if not eventtime:
            eventtime = datetime.now()
        if self.first == datetime.max:
            self.first = eventtime
        self.last = eventtime
        self.count += 1
        if path:
            head, *tail = path
            self.children[head].insert(tail)
        else:
            # print(self)
            self.events.append(eventtime)

    def find(self, path):
        path = self._splitpath(path)
        if path:
            head, *tail = path
            return self.children[head].find(tail)
        else:
            return self

    def getchildren(self, path=None):
        obj = self.find(path)
        return obj.children.keys()

    def getchildrenandcounts(self, path=None):
        obj = self.find(path)
        # print((path, obj))
        # print(obj.children.keys())
        return {k: obj.children[k].count for k in obj.children}

    def getchild(self, head):
        return self.children[head]

    def __str__(self):
        return (str(self.count) + ': ' + str(self.events) + '\n' +
                '\n'.join([k + ' ' + str(self.children[k]) for k in self.children]))

    def rollover(self, cutoff, callback=lambda x, y: None, prefix=None):
        if not prefix:
            prefix = []
        if self.first < cutoff:
            self.events.sort()
            while(self.events and self.events[0] < cutoff):
                callback(prefix, self.events.pop(0))
            for child in list(self.children.keys()):
                self.children[child].rollover(cutoff, callback, prefix + [child])
                if not self.children[child].count:
                    self.children.pop(child)
            self.count = len(self.events)
            if self.events:
                self.first = self.events[0]
                self.last = self.events[-1]
            else:
                self.first = datetime.max
                self.last = datetime.min
            for child in self.children.keys():
                self.count += self.children[child].count
                childfirst = self.children[child].first
                childlast = self.children[child].last
                if childfirst < self.first:
                    self.first = childfirst
                if childlast > self.last:
                    self.last = childlast

    def details(self, prefix='/'):
        detail_list = [(e, prefix) for e in self.events]
        for child in self.children:
            detail_list.extend(self.children[child].details(prefix + '/' + child))
        return detail_list


def test():
    t = TimedTrie()
    t.insert('/home/devel/')
    t.insert('/home/tdubois')
    t.insert('/home/devel/')
    t.insert('/home/tdubois/maven')
    cutoff = datetime.now()
    t.insert('/home/devel/')
    t.insert('/home/tdubois')
    t.insert('/home/devel/')
    # print(t)
    print(t.getchild('home').getchildrenandcounts())

    t2 = TimedTrie()
    t.rollover(cutoff, t2.insert)
    # print('t')
    # print(t)
    print(t.getchild('home').getchildrenandcounts())
    # print('t2')
    # print(t2)

    t.rollover(datetime.now())
    # print('t')
    # print(t)
    print(t.getchild('home').getchildrenandcounts())
