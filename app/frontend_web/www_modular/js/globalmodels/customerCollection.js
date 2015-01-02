define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'globalmodels/scrollCollection'
], function($, _, Backbone, contextModel, ScrollCollection) {
    CustomerModel = Backbone.Model;

    customerCollection = new ScrollCollection;
    customerCollection.url = function() {return '/customers'+this.offset+'-'+(this.offset+this.limit);};
    customerCollection.model = CustomerModel;
    customerCollection.limit = 10;

    customerCollection.initialize();

    return customerCollection;
});
