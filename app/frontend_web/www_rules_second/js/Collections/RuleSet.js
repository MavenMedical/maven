define([
    'jquery',
    'underscore',
    'backbone',
    'Models/Rule',
    
], function($, _, Backbone, Rule) {
    
    var RuleSet = Backbone.Collection.extend({
        model: Rule


    });
    return RuleSet;

});
