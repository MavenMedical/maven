##############################################################################
#  Copyright (c) 2014 - Maven Medical
#
#
#  Description: Generic cloud-side object to encapsulate an order
#               
#  Author: Tom DuBois - copied out of code by Aidan
#  Assumes: 
#  Side Effects: None
#  Last Modified: Monday February 10th - Aidan
##############################################################################

order_type = "orderType"
CPT = "CPT"
age = "age"
snomed_ids = "snomedIds"
dept = "dept"


class OrderObject():

    def __init__(self, order_id, order_parameters):
        self.order_id = order_id
        if (type(order_parameters[0]) != str):
            raise TypeError("The order type parameter must be a string")
        if (type(order_parameters[1]) != int):
            raise TypeError("The order CPT parameter must be an integer")
        if (type(order_parameters[2]) != int):
            raise TypeError("The age parameter must be an integer")
        if (type(order_parameters[3]) != list or type(order_parameters[3][0]) != int):
                raise TypeError("The snomed id parameter must be a list of integers")
        if (type(order_parameters[4]) != str):
            raise TypeError("The order department parameter must be a string")
        self.d = {
            order_type: order_parameters[0],
            CPT: order_parameters[1],
            age: order_parameters[2],
            snomed_ids: order_parameters[3],
            dept: order_parameters[4]
        }

    def __str__(self):
        return ', '.join(sorted(['{}->{}'.format(k, v) for k, v in self.d.items()]))