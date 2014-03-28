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
    'text!templates/widget/saving.html'
	], function ($, _, Backbone, currentContext, UtilizationModel, savingTemplate) {
	   
	   var Saving = Backbone.View.extend({
		   el: '.saving',
		   template: _.template(savingTemplate),
		   initialize: function(){
		       _.bindAll(this,'render');
		       this.utilization = new UtilizationModel;
		       this.render();
		   },
		   render: function () {
		       var that = this;
		       this.utilization.fetch({
			       success: function (util) {
				   that.$el.html(that.template({utilization:util}));
			       },
				   data: $.param(currentContext)
				   });
		   }
	       });
	   return Saving;
       });
