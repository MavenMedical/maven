#!/bin/bash
MAVEN_TESTING=1
export MAVEN_TESTING
echo $MAVEN_ROOT
cd $MAVEN_ROOT/clientApp/webservice
sleep 100 | nc -l 8090 | ${MAVEN_ROOT}/strip_ephemeral.bash&
sleep .1
python ${MAVEN_ROOT}/clientApp/webservice/client_server.py 2> /dev/null&
sleep .2
(cat test_message_from_ehr; sleep .1) | nc localhost 8088 &
sleep .2
kill -PIPE %sleep 
sleep .2
sleep 100 | nc -l 8090 | ${MAVEN_ROOT}/strip_ephemeral.bash&
sleep .2
(cat test_message_from_ehr; sleep .1) | nc localhost 8088 &
sleep .2
kill %python
kill %sleep
#kill %sleep

