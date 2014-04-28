#!/bin/bash
MAVEN_TESTING=1
export MAVEN_TESTING
cd $MAVEN_ROOT/clientApp/module_webservice
sleep 100 | nc -l 8090  &
sleep .1
python ${MAVEN_ROOT}/clientApp/module_webservice/client_server.py&
sleep .2
cat test_message_from_ehr | nc localhost 8088 &
sleep .2
#kill %sleep
kill %python