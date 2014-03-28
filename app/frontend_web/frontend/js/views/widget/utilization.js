/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
	// These are path alias that we configured in our main.js
	'jquery',     // lib/jquery/jquery
	'underscore', // lib/underscore/underscore
	'backbone',    // lib/backbone/backbone
	'currentContext',
	'models/utilizationModel',
	'text!templates/widget/utilization.html'
	], function ($, _, Backbone, currentContext, UtilizationModel, utilizationTemplate) {
	   
	   var Utilization = Backbone.View.extend({
		   el: '.utilization',
		   template: _.template(utilizationTemplate),
		   initialize: function(){
		       _.bindAll(this,'render');
		       this.utilization = new UtilizationModel;
		       this.render();
		   },
		   render: function () {
		       var that = this;
		       this.utilization.fetch({
			       success: function (util) {
				   that.$el.html(that.template({utilization:util , page: currentContext.page}));
			       },
				   data: $.param(currentContext)
				   });
		   }
	       });
	   return Utilization;
       });