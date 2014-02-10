##############################################################################
#  Copyright (c) 2014 - Maven Medical
#
#
#  Description: Generic cloud-side object to encapsulate our response to an order
#               
#  Author: Tom DuBois
#  Assumes: 
#  Side Effects: None
#  Last Modified: 
##############################################################################

import app.rule_engine.order_object as OO


class OrderResponseObject():

    def __init__(self, oid, response_priority, response_string):
        self.oid = oid
        self.response_string = response_string
        self.response_priority = response_priority
        self.hold_time = float("inf")

    def priority(self):
        return self.response_priority

    def text(self):
        return self.response_string