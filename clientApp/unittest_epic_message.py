import asyncio


class FakeMessageFromEpic(asyncio.Protocol):

    def connection_made(self, transport):
        self.transport = transport
        file = open('/home/devel/yukidev/maven/clientApp/fake_data/VistA_Encounter.xml')
        message = file.read()
        file.close()
        #message = "<Orders>    <Order>          <ProcedureCode>2345678</ProcedureCode>          <CodeType>Internal</CodeType>          <ExpectedDate>2011-01-01T00:00:00</ExpectedDate>          <ExpiredDate></ExpiredDate>          <Name>CBC with Automated Diff</Name>          <Type>Lab</Type>   </Order><Order>          <ProcedureCode>1234567</ProcedureCode>          <CodeType>Internal</CodeType>          <ExpectedDate>2011-01-01T00:00:00</ExpectedDate>          <ExpiredDate></ExpiredDate>          <Name>CBC with Automated Diff</Name>          <Type>Lab</Type>   </Order></Orders>"
        self.transport.write(message.encode())
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