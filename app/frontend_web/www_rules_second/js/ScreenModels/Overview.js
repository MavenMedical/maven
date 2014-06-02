define([
    'jquery',
    'underscore',
    'backbone',
    'ScreenModels/RuleListDisplay',
    'ScreenModels/RuleOverview',
    'Collections/RuleSet',
    'Helpers'

], function($, _, Backbone, RuleListDisplay, RuleOverview, RuleSet, Helpers) {

    var TopLevel = Backbone.Model.extend({

        defaults: {'RulePanel': new RuleListDisplay({'myRuleSet': new RuleSet(), 'myOverview': this}), 'RuleOverview': new RuleOverview()},
        initialize: function(){

            var temp = new RuleListDisplay({'myRuleSet': new RuleSet(), 'myOverview': this});

            this.set('RulePanel', temp);



        },
        addRuleToRulePanel: function(ruleIn){

            this.get('RulePanel').addRule(ruleIn);


        }

    });



    return TopLevel;

});
