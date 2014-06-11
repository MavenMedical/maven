/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/summaryModel', // current patient (if any)
    'globalmodels/patientModel',
    'globalmodels/contextModel',
], function ($, _, Backbone,  summaryModel, patientModel, contextModel) {
    
    var Summary = Backbone.View.extend({
	initialize: function(arg) {
	    this.template = _.template(arg.template); // this must already be loaded
	    this.update(summaryModel);
	    summaryModel.on('change', this.update, this);
	    contextModel.on('change:patients change:encounter', this.update, this);
	    patientModel.on('change:name', this.update, this);
	},
	update: function(summary) {
	    if(summaryModel.get('spending')) {
		var title = 'your patients';
		if(contextModel.get('encounter')) {
		    title = 'current encounter';
		} else if(contextModel.get('patients')) {
		    title = patientModel.get('name');
		}
		//console.log(title+": "+contextModel.get('encounter')+"  "+contextModel.get('patients'));
		//console.log(contextModel);
		this.$el.html(this.template($.extend({},summaryModel.attributes,{'title':title})));
		this.$el.show();
	    } else {
		this.$el.hide();
	    }
	}
    });
    return Summary;
});
