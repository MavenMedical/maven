/**
 * Created by Asmaa Aljuhani on 3/14/14.
 */

define([
    'jquery',
    'underscore',
    'backbone',
    'localmodels/patientModel',
    'globalmodels/contextModel'
], function($, _, Backbone, PatientModel, contextModel){
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
