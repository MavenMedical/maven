#!/bin/bash
echo $MAVEN_ROOT
cd $MAVEN_ROOT/clientApp/module_webservice
python ${MAVEN_ROOT}/clientApp/module_webservice/client_server.py 2> /dev/null&
sleep .2
cat bad_message_from_ehr | nc localhost 8088 | sed -e 's/\r//g' &
sleep .2
kill %python
#kill %sleep

