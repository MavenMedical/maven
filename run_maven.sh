#!/bin/bash
echo `date`
source /home/devel/.bashrc
echo ${MAVEN_ROOT}
cd ${MAVEN_ROOT}

nohup ${MAVEN_ROOT}/env/bin/python ${MAVEN_ROOT}/reporter/watcher.py &
nohup ${MAVEN_ROOT}/env/bin/python ${MAVEN_ROOT}/app/database/endpoint/database_endpoint.py &
sleep 1
nohup ${MAVEN_ROOT}/env/bin/python ${MAVEN_ROOT}/app/backend/webservices/data_router_all_svcs.py &
sleep 1
# ${MAVEN_ROOT}/env/bin/python ${MAVEN_ROOT}/clientApp/webservice/client_server.py &
nohup ${MAVEN_ROOT}/env/bin/python ${MAVEN_ROOT}/clientApp/webservice/clientapp_main_server.py &
sleep 1
nohup ${MAVEN_ROOT}/env/bin/python ${MAVEN_ROOT}/app/backend/evaluators/composition_evaluator.py &


