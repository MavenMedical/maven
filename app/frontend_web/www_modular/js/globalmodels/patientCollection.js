define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel'
], function($, _, Backbone, contextModel){
    var PatientModel = Backbone.Model;

    var PatientCollection = Backbone.Collection.extend({
	url: '/patients',
	model: PatientModel,
	initialize: function(){
            // nothing here yet
        },
    });

    patientCollection = new PatientCollection;
    if(contextModel.get('userAuth')) {
	patientCollection.fetch({data:$.param(contextModel.toJSON())});
    }
    contextModel.on('change', 
		    // this will be needed once the context filters things
		    function(cm) {
			if(false && cm.get('userAuth')) {
			    patientCollection.fetch({data:$.param(contextModel.toJSON())});
			}
		    }, patientCollection);
    return patientCollection;
});
