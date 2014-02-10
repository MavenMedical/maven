##############################################################################
#  Copyright (c) 2014 - Maven Medical
#
#
#  Description: Generic cloud-side object to encapsulate an order
#               
#  Author: Tom DuBois - copied out of code by Aidan
#  Assumes: 
#  Side Effects: None
#  Last Modified: 
##############################################################################

order_type = "orderType"
CPT = "CPT"
age = "age"
snomed_ids = "snomedIds"
dept = "dept"


class OrderObject():

    def __init__(self, order_id, order_parameters):
        self.order_id = order_id
        self.d = {
            order_type: order_parameters[0],
            CPT: order_parameters[1],
            age: order_parameters[2],
            snomed_ids: order_parameters[3],
            dept: order_parameters[4]
        }

    def __str__(self):
        return ', '.join(sorted(['{}->{}'.format(k, v) for k, v in self.d.items()]))
