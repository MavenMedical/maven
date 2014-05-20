/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel', // current patient (if any)
    'text!templates/patientSearch.html'
], function ($, _, Backbone,  contextModel, patSearchTemplate) {
    
    var PatInfo = Backbone.View.extend({
	template: _.template(patSearchTemplate),
	initialize: function(){
	    this.update(contextModel);
	    contextModel.on('change:patients', this.update, this);
	},
	update: function(cm) {
	    if(cm.get('patients')) {
		// for now this is what we do when there is no patient selected
		//this.$el[0].style.display='none';
	    } else {
		//this.$el[0].style.display='';
		this.$el.html(this.template(contextModel.attributes));
	    }
	}
    });
    return PatInfo;
});
