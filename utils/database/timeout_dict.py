# NOTE - timeout_dict was written for using the the polling notification service
# We ended up using something else, so this code is dead.  I'm keeping it around
# because it might be good for something later
import asyncio


class _self_destruct_task(asyncio.Task):
    def __init__(self, destroy_fn, timeout):
        asyncio.Task.__init__(self, self.destroy(timeout))
        self.destroy_fn = destroy_fn
        self.data = []

    def __repr__(self):
        return str(self.data)

    @asyncio.coroutine
    def destroy(self, timeout):
        yield from asyncio.sleep(timeout)
        self.destroy_fn()

    def reap(self):
        self.cancel()
        self.destroy_fn()
        return self.data

    def append(self, d):
        self.data.append(d)


class TimeoutDict:
    def __init__(self, expire_fn, timeout):
        self.map = {}
        self.timeout = timeout
        self.expire_fn = expire_fn

    def __contains__(self, key):
        return key in self.map

    def get(self, key):
        return self.map[key].data

    def pop(self, key):
        v = self.map[key].data
        self.map[key].cancel()
        self.map.pop(key)
        return v

    def put(self, key, value):
        if key in self.map:
            self.map[key].cancel()
        self.map[key] = _self_destruct_task(lambda: self.expire_fn(key, self.map.pop(key)),
                                            self.timeout)
        self.map[key].data = value

    def append(self, key, value):
        if key in self.map:
            old = self.pop(key)
        else:
            old = []
        old.append(value)
        self.put(key, old)

    def extend(self, key, value):
        if key in self.map:
            old = self.pop(key)
        else:
            old = []
        old.extend(value)
        self.put(key, old)
