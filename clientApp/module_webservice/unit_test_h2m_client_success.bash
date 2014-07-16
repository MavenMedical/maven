#!/bin/bash
MAVEN_TESTING=1
export MAVEN_TESTING
cd $MAVEN_ROOT/clientApp/module_webservice
sleep 100 | nc -l 8090 | ${MAVEN_ROOT}/strip_ephemeral.bash &
sleep .1
python ${MAVEN_ROOT}/clientApp/module_webservice/client_server.py 2> /dev/null&
sleep .2
(sleep .3; cat test_message_from_ehr) | nc localhost 8088 &
sleep .2
#kill %sleep
kill %python
