define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel'
], function($, _, Backbone, contextModel){
    var PatientModel = Backbone.Model;

    var PatientCollection = Backbone.Collection.extend({
	//url: '/patients',
	url: function() {return '/patients/'+this.offset+'-'+(this.offset+this.limit);},
    limit: 10,
    tried: 0,
    offset: 0,
    model: PatientModel,
	initialize: function(){
            // nothing here yet
        },
    more: function() {
	    if(this.tried <= this.models.length) {
            this.offset = this.models.length;
            this.tried = this.models.length+this.limit;
            patientCollection.fetch({
                data:$.param(contextModel.toParams()),
                remove:false});
            }
	    },
    });

    patientCollection = new PatientCollection;
    if(contextModel.get('userAuth')) {
	patientCollection.fetch({data:$.param(contextModel.toParams())});
    }
    contextModel.on('change', 
		    // this will be needed once the context filters things
		    function(cm) {
			if(false && cm.get('userAuth')) {
			    patientCollection.fetch({data:$.param(contextModel.toParams())});
			}
		    }, patientCollection);
    return patientCollection;
});
