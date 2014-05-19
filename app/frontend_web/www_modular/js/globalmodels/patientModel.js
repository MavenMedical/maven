/**
 * Created by Asmaa Aljuhani on 3/14/14.
 */

define([
    'jquery',
    'backbone',
    'globalmodels/contextModel'
], function ($, BackBone, contextModel) {

    var PatientModel = Backbone.Model.extend({urlRoot: '/patient_details'});
    var patientModel = new PatientModel;

    if(contextModel.get('patients') && contextModel.get('userAuth')) {
	patientModel.fetch({data:$.param(contextModel.toJSON())});
    }
    contextModel.on('change:patients change:userAuth', 
		    function(x) {
			if(x.get('patients') != patientModel.get('id') 
			  && x.get('userAuth')) {
			    if(x.get('patients')) {
				patientModel.fetch({data:$.param(x.toJSON())});
			    } else {
				patientModel.set({id:''});
			    }
			}
		    });

    return patientModel;
});
