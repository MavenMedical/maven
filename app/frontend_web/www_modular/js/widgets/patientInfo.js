/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/patientModel', // current patient (if any)
], function ($, _, Backbone,  patientModel) {
    
    var PatInfo = Backbone.View.extend({
	initialize: function(arg) {
	    this.template = _.template(arg.template);
	    this.update(patientModel);
	    patientModel.on('change', this.update, this);
	},
	update: function(pat) {
	    if(patientModel.get('id')) {
		this.$el.html(this.template(patientModel.attributes));
	    } else {
		// for now this is what we do when there is no patient selected
	    }
	}
    });
    return PatInfo;
});
