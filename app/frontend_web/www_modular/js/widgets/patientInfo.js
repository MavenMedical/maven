/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/patientModel', // current patient (if any)
    'text!templates/patientInfo.html'
], function ($, _, Backbone,  patientModel, patInfoTemplate) {
    
    var PatInfo = Backbone.View.extend({
	template: _.template(patInfoTemplate),
	initialize: function(){
	    this.update(patientModel);
	    patientModel.on('change', this.update, this);
	},
	update: function(pat) {
	    if(patientModel.get('id')) {
		this.$el[0].style.display='';
		this.$el.html(this.template(patientModel.attributes));
	    } else {
		// for now this is what we do when there is no patient selected
		this.$el[0].style.display='none';
	    }
	}
    });
    return PatInfo;
});
