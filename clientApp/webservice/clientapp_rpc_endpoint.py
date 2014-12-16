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
import clientApp.allscripts.allscripts_customer_interface as ACI
import maven_logging as ML


class ClientAppEndpoint():

    def __init__(self, server_interface, loop=None):
        self.customer_interfaces = {}
        self.server_interface = server_interface
        self.loop = loop or asyncio.get_event_loop()

    @asyncio.coroutine
    def update_customer_configuration(self, customer_id, config):

        if customer_id in self.customer_interfaces:
            yield from self.customer_interfaces[customer_id].update_config(config)
            return True
        else:
            if not config:
                return
            aci = ACI.AllscriptsCustomerInterface(customer_id, config,
                                                  self.server_interface)
            yield from aci.validate_config()  # raises on failure
            yield from aci.start()
            self.customer_interfaces[customer_id] = aci

    @asyncio.coroutine
    def test_customer_configuration(self, customer_id, config):
        aci = ACI.AllscriptsCustomerInterface(customer_id, config,
                                              self.server_interface)
        yield from aci.validate_config()  # raises on failure
        yield from self.update_customer_configuration(customer_id, config)

    @asyncio.coroutine
    def notify_user(self, customer_id, user_name, subject, msg, patient=None, target=None):
        customer_interface = self.customer_interfaces[customer_id]
        ML.report('/%s/nofify/%s/%s' % (customer_id, user_name, target))
        yield from customer_interface.notify_user(user_name, patient, subject,
                                                  msg, target or user_name)

    @asyncio.coroutine
    def handle_evaluated_composition(self, customer_id, composition):
        customer_interface = self.customer_interfaces[customer_id]
        yield from customer_interface.handle_evaluated_composition(composition)

    @asyncio.coroutine
    def update_user_state(self, customer_id, user_name, state):
        customer_interface = self.customer_interfaces[customer_id]
        customer_interface.update_user(user_name, state)
