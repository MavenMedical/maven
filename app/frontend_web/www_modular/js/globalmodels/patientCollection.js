define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'globalmodels/scrollCollection'
], function($, _, Backbone, contextModel, ScrollCollection){
    var PatientModel = Backbone.Model;

    patientCollection = new ScrollCollection;
    patientCollection.url = function() {return '/patients'+this.offset+'-'+(this.offset+this.limit);};
    patientCollection.model = PatientModel;
    patientCollection.limit = 10;
    patientCollection.context = function(){
      contextModel.on('change:patients change:startdate change:enddate',
		    // this will be needed once the context filters things
		    function(cm) {
			if(true && cm.get('userAuth')) {
			    this.tried = 0;
			    this.offset=0;
			    patientCollection.fetch({
				data:$.param(contextModel.toParams()),
				remove:true});
			}
	    }, this);
    };
    patientCollection.initialize();

    return patientCollection;
});
