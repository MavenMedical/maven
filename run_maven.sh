#!/bin/bash
echo `date`
echo ${MAVEN_ROOT}
${MAVEN_ROOT}/env/bin/python ${MAVEN_ROOT}/app/backend/webservices/data_router_all_svcs.py &
sleep 1
# ${MAVEN_ROOT}/env/bin/python ${MAVEN_ROOT}/clientApp/webservice/client_server.py &
${MAVEN_ROOT}/env/bin/python ${MAVEN_ROOT}/clientApp/webservice/clientapp_main_server.py &
sleep 1
${MAVEN_ROOT}/env/bin/python ${MAVEN_ROOT}/app/backend/evaluators/composition_evaluator.py &


