#!/bin/bash
python /home/devel/yukidev/maven/app/backend/module_webservice/data_router.py &
sleep 1
python /home/devel/yukidev/maven/clientApp/module_webservice/client_server.py &
sleep 1
python /home/devel/yukidev/maven/app/backend/module_cost_evaluator/cost_evaluator.py &
sleep 1
python /home/devel/yukidev/maven/clientApp/unittest.py &
sleep 1
