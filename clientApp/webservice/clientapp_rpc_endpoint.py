# *************************************************************************
# Copyright (c) 2014 - Maven Medical
# ************************
# AUTHOR:
__author__ = 'Yuki Uchino'
# ************************
# DESCRIPTION:
#
#
#
#
# ************************
# ASSUMES:
# ************************
# SIDE EFFECTS:
# ************************
# LAST MODIFIED FOR JIRA ISSUE: MAV-404
# *************************************************************************
import asyncio
import json
import clientApp.allscripts.allscripts_customer_interface as ACI


class ClientAppEndpoint():

    def __init__(self, server_interface, loop=None):
        self.customer_interfaces = {}
        self.server_interface = server_interface
        self.loop = loop or asyncio.get_event_loop()

    @asyncio.coroutine
    def update_customer_configuration(self, customer_id, config):
        config = json.loads(config)
        if customer_id in self.customer_interfaces:
            yield from self.customer_interfaces[customer_id].test_and_update_config(config)
        else:
            aci = ACI.AllscriptsCustomerInterface(customer_id, config,
                                                  self.server_interface)
            config_isValid = yield from aci.validate_config()
            if config_isValid:
                yield from aci.start()
                self.customer_interfaces[customer_id] = aci
            else:
                return False  # Need to do some error handling here/warn the IT Admin that connection wasn't successful
        return

    @asyncio.coroutine
    def test_customer_configuration(self, customer_id, config):
        try:
            aci = ACI.AllscriptsCustomerInterface(customer_id, config,
                                                  self.server_interface)
            if aci.validate_config():
                self.update_customer_configuration(customer_id, config)
                return True
        except:
            return False

    @asyncio.coroutine
    def notify_user(self, customer_id, user_name, msg):
        customer_interface = self.customer_interfaces[customer_id]
        yield from customer_interface.notify_user(user_name, msg)
