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
# import clientApp.webservice.allscripts_client_app as ALLSCRIPTS_CA


class AllscriptsCustomerInterface:
    def __init__(self, config):
        pass

    @asyncio.coroutine
    def test_connection(self):
        pass


class ClientAppEndpoint():

    def __init__(self, remote_procedures, loop=None):
        self.customer_interfaces = {}
        self.remote_procedures = remote_procedures
        self.loop = loop or asyncio.get_event_loop()

    @asyncio.coroutine
    def update_customer_configuration(self, customer_id, config):
        if customer_id in self.customer_interfaces:
            yield from self.customer_interfaces[customer_id].test_and_update_config(config)
        else:
            aci = AllscriptsCustomerInterface(config)
            yield from aci.test_connection()
            self.customer_interfaces[customer_id] = aci
        return

    @asyncio.coroutine
    def test_customer_configuration(self, customer_id):
        try:
            self.customer_interfaces[customer_id].test()
            return True
        except:
            return False
