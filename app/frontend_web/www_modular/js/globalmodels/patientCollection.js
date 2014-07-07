define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'globalmodels/scrollCollection'
], function($, _, Backbone, contextModel, ScrollCollection){
    var PatientModel = Backbone.Model;

    patientCollection = new ScrollCollection;
    patientCollection.url = function() {return '/patients/'+this.offset+'-'+(this.offset+this.limit);};
    patientCollection.model = PatientModel;
    patientCollection.limit = 10;
    patientCollection.initialize();

    return patientCollection;
});
