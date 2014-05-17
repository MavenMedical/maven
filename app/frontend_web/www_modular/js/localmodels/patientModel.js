/**
 * Created by Asmaa Aljuhani on 3/14/14.
 */

define([
    'backbone'
], function (Backbone) {
    
    var PatientModel = Backbone.Model.extend({
	urlRoot: '/patient_details',
	defaults: {
	    name: "Batman",
	    gender: "Male",
	    DOB: "05/03/1987",
	    dx: "Asthma",
	    cost: "-1"
	},
	initialize: function() {
	}
    });
    
    // models in globalmodels return an instance (not a constructor)
    return PatientModel;
    
});
