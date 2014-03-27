#!/bin/bash
python3 /home/ec2-user/maven/app/backend/module_webservice/data_router.py &
sleep 1
python3 /home/ec2-user/maven/clientApp/module_webservice/client_server.py &
sleep 1
python3 /home/ec2-user/maven/app/backend/module_cost_evaluator/cost_evaluator.py &
sleep 1

