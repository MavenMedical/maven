/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/summaryModel', // current patient (if any)
    'globalmodels/contextModel',
    'text!templates/encounterSummary.html'
], function ($, _, Backbone,  summaryModel, contextModel, encSummaryTemplate) {
    
    var Summary = Backbone.View.extend({
	template: _.template(encSummaryTemplate),
	initialize: function(){
	    this.update(summaryModel);
	    summaryModel.on('change', this.update, this);
	    contextModel.on('change:patientName change:encounter', this.update, this);
	},
	update: function(summary) {
	    if(summaryModel.get('spending')) {
		var title = 'your patients';
		if(contextModel.get('encounter')) {
		    title = 'current encounter';
		} else if(contextModel.get('patients')) {
		    title = contextModel.get('patientName');
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
