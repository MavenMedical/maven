import asyncio


class FakeMessageFromEpic(asyncio.Protocol):

    def connection_made(self, transport):
        self.transport = transport
        file = open('/home/devel/yukidev/maven/clientApp/module_webservice/GetEncounterCharges_Response.xml')
        message = file.read().encode()
        file.close()
        self.transport.write(message)
        self.transport.close()


    def connection_lost(self, exc):
        print('server closed the connection')
        asyncio.get_event_loop().stop()

    def data_received(self, data):
        print(data)


loop = asyncio.get_event_loop()
msg_coro = loop.create_connection(FakeMessageFromEpic, '127.0.0.1', 12345)
loop.run_until_complete(msg_coro)
loop.run_forever()
loop.close()
