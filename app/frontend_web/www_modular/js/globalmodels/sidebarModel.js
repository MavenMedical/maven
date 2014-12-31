/**
 * Created by devel on 11/19/14.
 */
define([
    'backbone'
],
       function(Backbone) {
           var details = {
               'Profile':['fa-user', 'profile'],
               'Customers':['fa-user', 'customers'],
               'Pathways':['fa-user', 'pathways'],
               'Pathway Mgmt': ['fa-cloud', 'pathway', [
                   {'Pathway Viewer': ['icon', 'pathway']},
                   {'Pathway Editor': ['icon', 'pathwayEditor']}]],
               'Dashboard': ['fa-tachometer', 'home']
           }
           
	   var SidebarModel = Backbone.Model.extend({
               
	       addOption: function(name) {
                   if (!this.get(name)) {
                       this.set(name, details[name]) 
                   }
               }
           })
           
	   return new SidebarModel
       })      
