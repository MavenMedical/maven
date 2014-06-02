
define([
    'jquery',
    'underscore',
    'backbone',
    'bootstrap',

    //Models
    'Models/Rule',
    'ScreenModels/Overview',

    //Views
    'Views/OverviewView',


    'Helpers'


], function ($, _, Backbone, Bootstrap, Rule, /*Models*/Overview,/*Views*/ OverviewView,  Helpers) {
    var initialize = function () {
        var testTopLevelModel = new Overview();

        testTopLevelModel.addRuleToRulePanel(new Rule({name: "rule1"}));
        testTopLevelModel.addRuleToRulePanel(new Rule({name: "rule4"}));

        var testTopLevel = new OverviewView({model: testTopLevelModel});

        testTopLevel.render();


    };

    return {
        initialize: initialize
    };
});