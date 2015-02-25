/**
 * Created by devel on 11/19/14.
 */
define([
    'backbone',
    'globalmodels/contextModel'
],
       function(Backbone, contextModel) {
           var details = {
               'Profile':{icon:'fa-user', page:'profile'},
               'Customers':{icon:'fa-user', page:'customers'},
               'Pathways':{icon:'fa-user', page:'pathways'},
               'Pathway Mgmt': {icon:'fa-cloud', page:'pathwayeditor', children:[
                   {'Pathway Editor': {icon:'icon', page:'pathwayEditor'}}, 
                   {'Pathway Viewer': {icon:'icon', page:'pathway',
                                      init: 
                                       function(el) {
                                           console.log(contextModel)
                                           contextModel.on('change:pathid', 
                                                           function() {
                                                               if(contextModel.get('pathid')) {
                                                                   el.show()
                                                               } else {
                                                                   el.hide()
                                                               }});
                                       if (contextModel.get('pathid')) {
                                           el.show()
                                       } else {
                                           el.hide()
                                       }}
                                      }}]},
               'Dashboard': {icon:'fa-tachometer', page:'home'}
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
