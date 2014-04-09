#!/bin/bash
~/maven/env/bin/python ~/maven/app/backend/module_webservice/data_router.py &
sleep 1
~/maven/env/bin/python ~/maven/clientApp/module_webservice/client_server.py &
sleep 1
~/maven/env/bin/python ~/maven/app/backend/module_cost_evaluator/cost_evaluator.py &
sleep 1
~/maven/env/bin/python ~/maven/app/frontend_web/rest_interface/web_services.py &

