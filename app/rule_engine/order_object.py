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

orderType = "orderType"
CPT="CPT"
age="age"
snomedIds="snomedIds"
dept="dept"

class OrderObject():
	def __init__(self,orderParameters):
		self.d = {}
		self.d[orderType] = orderParameters[0]
		self.d[CPT] = orderParameters[1]
		self.d[age] = orderParameters[2]
		self.d[snomedIds] = orderParameters[3]
		self.d[dept] = orderParameters[4]

	def __str__(self):
		return ', '.join(['{}->{}'.format(k,v) for k,v in self.d.items()])
