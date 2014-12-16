#!/bin/bash
source /home/devel/.bashrc
cd ${MAVEN_ROOT}

nohup ${MAVEN_ROOT}/env/bin/python ${MAVEN_ROOT}/app/database/endpoint/database_endpoint.py &
sleep 2
nohup ${MAVEN_ROOT}/env/bin/python ${MAVEN_ROOT}/app/backend/evaluators/composition_evaluator.py &