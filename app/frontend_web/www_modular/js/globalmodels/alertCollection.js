define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'globalmodels/scrollCollection'
], function($, _, Backbone, contextModel, ScrollCollection) {
    AlertModel = Backbone.Model;

    alertCollection = new ScrollCollection;
    alertCollection.url = function() {return '/alerts/'+this.offset+'-'+(this.offset+this.limit);};
    alertCollection.model = AlertModel;
    alertCollection.limit = 5;
    alertCollection.initialize();

    return alertCollection;
});
