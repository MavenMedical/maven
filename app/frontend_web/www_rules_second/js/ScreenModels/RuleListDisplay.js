define([
    'jquery',
    'underscore',
    'backbone',
    'Collections/RuleSet',

    'Helpers'

], function($, _, Backbone, RuleSet, Helpers) {

    var RuleOverview = Backbone.Model.extend({

        defaults: {'myRuleSet': new RuleSet()},
        addRule: function(params){
            this.get('myRuleSet').addRule(params);
        },
        deleteRule: function(toDelete){
          console.log(this.get('myRuleSet').length);
          this.get('myRuleSet').remove(toDelete);
          console.log(this.get('myRuleSet').length);
        }
    });
    return RuleOverview;

});
