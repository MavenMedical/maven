define([
    'jquery',
    'underscore',
    'backbone',
    'Models/Rule',
    
], function($, _, Backbone, Rule) {
    
    var RuleSet = Backbone.Collection.extend({
        model: Rule,

        addRule: function(params){

            var newRule = new Rule(params);
            this.add(newRule);
        }
    });
    return RuleSet;

});
