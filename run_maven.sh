#!/bin/bash
echo `date`
echo ${MAVEN_ROOT}
${MAVEN_ROOT}/env/bin/python ${MAVEN_ROOT}/app/backend/webservices/data_router.py &
sleep 1
${MAVEN_ROOT}/env/bin/python ${MAVEN_ROOT}/clientApp/webservice/client_server.py &
${MAVEN_ROOT}/env/bin/python ${MAVEN_ROOT}/clientApp/webservice/allscripts_server.py &
sleep 1
${MAVEN_ROOT}/env/bin/python ${MAVEN_ROOT}/app/backend/evaluators/composition_evaluator.py &
sleep 1
${MAVEN_ROOT}/env/bin/python ${MAVEN_ROOT}/app/frontend_web/rest_interface/web_services.py &

