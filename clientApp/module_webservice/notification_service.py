import asyncio
import asyncio.queues
import json
from collections import defaultdict

import maven_logging as ML
import maven_config as MC
import utils.streaming.http_responder as HR
import utils.streaming.stream_processor as SP

QS_KEY = 'key'
CONFIG_QUEUEDELAY = 'queue delay'

RESPONSE_TEXT = 'TEXT'
RESPONSE_LINK = 'LINK'

class NotificationService(HR.HTTPProcessor):
    def __init__(self, configname):
        HR.HTTPProcessor.__init__(self,configname)
        self.add_handler(['GET'], '/poll', self.get_poll)
#        self.add_handler(['GET'], '/post', self.get_post)
        self.message_queues = defaultdict(asyncio.queues.Queue)
        self.queue_delay = self.config.get(CONFIG_QUEUEDELAY, 0)
        
    @asyncio.coroutine
    def get_poll(self, _header, _body, qs, _matches, _key):
        ret=[]  # build the list of pending messages here.  
        key = qs[QS_KEY][0]
        queue = self.message_queues[key]
        if not queue.qsize():  # if there are no messages ready to display, wait for one
            f=asyncio.async(queue.get())
            try:
                y = yield from asyncio.wait_for(f, self.queue_delay, loop=self.loop)  # wait for a message
                ret.append(y)
            except:
                f.cancel()  # wait_for does not cancel the future, so do that explicitly upon any error
        try:
            while True:  # read and append all available messages on the queue
                ret.append(queue.get_nowait())
        except:
            pass
        return (HR.OK_RESPONSE, json.dumps([self._convert_message(x) for x in ret]), None)

    @asyncio.coroutine
    def get_post(self, _header, _body, qs, _matches, _key):
        key = qs[QS_KEY][0]
        message = qs['message'][0]
        self.send_messages(key, [message])
        return (HR.OK_RESPONSE, b'', None)
    
    def _convert_message(self, message):
        m = message.split('\n',1)
        if len(m)==2:
            return {
                RESPONSE_TEXT: m[1],
                RESPONSE_LINK: m[0],
                }
        else:
            return {
                RESPONSE_TEXT: message,
                RESPONSE_LINK: 'http://www.google.com',
                }

    def send_messages(self, key, messages=None):
        if key in self.message_queues:
            if messages:
                for message in messages:
                    self.message_queues[key].put_nowait(message)
            return True
        else:
            return False
                    
if __name__ == '__main__':
    ML.DEBUG = ML.stdout_log
    MC.MavenConfig = {
        'notificationserver':
        {
            SP.CONFIG_HOST: 'localhost',
            SP.CONFIG_PORT: 8091,
            SP.CONFIG_PARSERTIMEOUT: 120,
            CONFIG_QUEUEDELAY: 10,
        },
    }
    
    hp = NotificationService('notificationserver')
    event_loop = asyncio.get_event_loop()
    hp.schedule(event_loop)
    event_loop.run_forever()

