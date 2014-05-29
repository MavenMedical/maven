define([
    'jquery',
    'underscore',
    'backbone',
    'ScreenModels/RuleListDisplay',
    'ScreenModels/RuleOverview',
    'Helpers'

], function($, _, Backbone, RuleListDisplay, RuleOverview, Helpers) {

    var TopLevel = Backbone.Model.extend({

        defaults: {'RulePanel': new RuleListDisplay(), 'RuleOverview': new RuleOverview()},
        addRuleToRulePanel: function(params){

;
            this.get('RulePanel').addRule(params);


        }

    });



    return TopLevel;

});
