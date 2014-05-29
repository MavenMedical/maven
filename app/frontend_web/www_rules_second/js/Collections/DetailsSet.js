define([
    'jquery',
    'underscore',
    'backbone',
    'Models/Detail',

], function($, _, Backbone, Detail) {
    
    var DetailsSet = Backbone.Collection.extend({
        model: Detail
    });
    
    
    
    return DetailsSet;

});
