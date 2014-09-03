#!/bin/bash
MAVEN_TESTING=1
export MAVEN_TESTING
echo $MAVEN_ROOT
cd $MAVEN_ROOT/clientApp/webservice
sleep 100 | nc -l 8090 2>/dev/null&
sleep .1
python ${MAVEN_ROOT}/clientApp/webservice/client_server.py 2> /dev/null&
sleep .2
(cat bad_message_from_ehr; sleep .3) | nc localhost 8088 | sed -e 's/\r//g' &
sleep .2
kill %python
#kill %sleep
