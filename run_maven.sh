#!/bin/bash
python3 ~/maven/app/backend/module_webservice/data_router.py &
sleep 1
python3 ~/maven/clientApp/module_webservice/client_server.py &
sleep 1
python3 ~/maven/app/backend/module_cost_evaluator/cost_evaluator.py &
sleep 1
python3 ~/maven/app/frontend_web/rest_interface/web_services.py &

