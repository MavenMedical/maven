#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
__author__='Tom DuBois'
#************************
#DESCRIPTION:
# This file contains the core web services to deliver json objects to the 
# frontend website
#************************
#*************************************************************************

import app.utils.streaming.stream_processor as SP
import app.utils.streaming.http_responder as HTTP
import asyncio
import asyncio.queues
import json
import maven_logging as ML
import maven_config as MC

class MessagingWebService(HTTP.HTTPProcessor):
    
    def __init__(self, configname):
        HTTP.HTTPProcessor.__init__(self,configname)

        self.add_handler(['POST'], '/send', self.post_message)
        self.add_handler(['GET'], '/recv', self.recv_message)
        self.messages=asyncio.queues.Queue()

    @asyncio.coroutine
    def post_message(self, _header, body, _qs, _matches, _key):
        body=body.decode('utf-8')
        print(body)
        print(len(self.messages._getters))
        self.messages.put_nowait(body)
        print(">>>>>>>>>>>>> message queue of size "+str(self.messages.qsize()))
        print(len(self.messages._getters))
        return (HTTP.OK_RESPONSE, b'', None)

    @asyncio.coroutine
    def recv_message(self, _header, _body, _qs, _matches, _key):
        ret=''
        if not self.messages.qsize():
            f=asyncio.async(self.messages.get())
            try:
                ret = yield from asyncio.wait_for(f, 4, loop=self.loop)
                print(">>>>>>>>>>>> got message from queue")
            except:
                f.cancel()
        else:
            ret = self.messages.get_nowait()
            try:
                while True:
                    ret = '\n'.join([ret,self.messages.get_nowait()])
            except:
                pass
        yield from asyncio.sleep(.5)
        return (HTTP.OK_RESPONSE, json.dumps(ret), None)

#        return (HTTP.OK_RESPONSE, b'some text', None)

if __name__ == '__main__':
    ML.DEBUG = ML.stdout_log
    MC.MavenConfig = {
        "httpserver":
            {
            SP.CONFIG_HOST: 'localhost',
            SP.CONFIG_PORT: 8087,
            },
        }
    
    hp = MessagingWebService('httpserver')
    event_loop = asyncio.get_event_loop()
    hp.schedule(event_loop)
    event_loop.run_forever()



"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>BackboneTutorials.com Beginner Video</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/2.1.1/css/bootstrap.min.css">
</head>

<body onload="recvFunction()">

  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/1.8.2/jquery.min.js" type="text/javascript"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/underscore.js/1.4.2/underscore-min.js" type="text/javascript"></script>
  <script type="text/javascript">
    function sendFunction(v) {
     $.ajax({type: "POST",
          url: "services/send",
               data: v,
                    dataType: 'text/plain'});
   };

   function recvFunction2() {
     $.getJSON("services/recv", '', function(result){alert(result);});
   };

   function recvFunction() {
     $.ajax({type:'GET',
          url:"services/recv",
               dataType:'json'})
     .done(function(data) {
       console.log(data)
       //$("div#output").update(data);
       document.getElementById("output").textContent=data;
       return recvFunction();
     })
     .fail(function(RQ, status, error) {
       console.log(RQ);
       console.log(status);
       console.log(error);
     });
   };
     
   

  </script>
  
    <form class="edit-user-form">
      <label>Enter Text</label>
      <input name="message" type="text">
      <hr />
      <button type="button" class="btn" onclick="sendFunction(message.value)">Send</button>
    </form>

    <div id='output'>
      Some other text here.
    </div>

</body>
</html> 
"""
