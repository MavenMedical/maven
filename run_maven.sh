#!/bin/bash
echo `date`
echo ${MAVEN_ROOT}
${MAVEN_ROOT}/env/bin/python ${MAVEN_ROOT}/app/backend/webservices/data_router.py &
sleep 1
${MAVEN_ROOT}/env/bin/python ${MAVEN_ROOT}/clientApp/module_webservice/client_server.py &
sleep 1
${MAVEN_ROOT}/env/bin/python ${MAVEN_ROOT}/app/backend/evaluators/cost_evaluator.py &
sleep 1
${MAVEN_ROOT}/env/bin/python ${MAVEN_ROOT}/app/frontend_web/rest_interface/web_services.py &

