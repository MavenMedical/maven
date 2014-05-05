#!/bin/bash
MAVEN_TESTING=1
export MAVEN_TESTING
echo $MAVEN_ROOT
cd $MAVEN_ROOT/clientApp/module_webservice
sleep 100 | nc -l 8090 2>/dev/null | ${MAVEN_ROOT}/strip_ephemeral.bash&
sleep .1
python ${MAVEN_ROOT}/clientApp/module_webservice/client_server.py&
sleep .2
cat test_message_from_ehr | nc localhost 8088 &
sleep .2
kill -PIPE %sleep 
sleep .2
sleep 100 | nc -l 8090 | ${MAVEN_ROOT}/strip_ephemeral.bash&
sleep .5
cat test_message_from_ehr | nc localhost 8088 &
sleep .2
kill %python
#kill %sleep
