#!/bin/bash
echo $MAVEN_ROOT
cd $MAVEN_ROOT/clientApp/module_webservice
sleep 100 | nc -l 8090 2>/dev/null&
sleep .1
python ${MAVEN_ROOT}/clientApp/module_webservice/client_server.py&
sleep .2
cat bad_message_from_ehr | nc localhost 8088 &
sleep .2
kill %python
#kill %sleep

