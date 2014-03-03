##############################################################################
#  Copyright (c) 2014 - Maven Medical
#
#
#  Description: Launch the response aggregator
#               
#  Author: Tom DuBois
#  Assumes: 
#  Side Effects: None
#  Last Modified: 
##############################################################################

#import app.rule_engine.order_response_object as RE
import app.backend.module_rule_engine.order_response_object as ORO
import app.utils.streaming.stream_processor as SP
import app.backend.module_rule_engine.response_aggregator as RA
import time
import maven_config as MC
import pickle
from maven_logging import PRINT
import asyncio

ra_name = "response aggregator"
MavenConfig = {
    ra_name:
    {
        SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
        SP.CONFIG_WRITERNAME: ra_name+".writer",
        SP.CONFIG_READERNAME: ra_name+".reader",
        SP.CONFIG_READERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
        RA.CONFIG_RESPONSE_HOLD_TIME: .5,
        RA.CONFIG_EXPIRATION_MEMORY: 1024,
        SP.CONFIG_WAKESECONDS: .05,
    },
    ra_name+'.writer':
    {
        SP.CONFIG_HOST:'localhost',
        SP.CONFIG_QUEUE:'aggregated response queue',
        SP.CONFIG_EXCHANGE:'maven_exchange',
        SP.CONFIG_KEY:'incoming',
    },
    ra_name+".reader":
    {
        SP.CONFIG_HOST:'localhost',
        SP.CONFIG_QUEUE:'response_queue',
        SP.CONFIG_EXCHANGE:'maven_exchange',
        SP.CONFIG_KEY:'incoming'
    },
 

}
MC.MavenConfig = MavenConfig

# do argument parsing here and adjust configuration parameters as needed

loop=asyncio.get_event_loop()
ra = RA.ResponseAggregator(ra_name)
ra.schedule(loop)
