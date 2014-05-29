
define([
    'jquery',
    'underscore',
    'backbone',
    'bootstrap',

    //Models
    'ScreenModels/Overview',

    //Views
    'Views/OverviewView',


    'Helpers'


], function ($, _, Backbone, Bootstrap, /*Models*/Overview,/*Views*/ OverviewView,  Helpers) {
    var initialize = function () {
        var testTopLevelModel = new Overview();

        testTopLevelModel.addRuleToRulePanel({name: "rule1"});
        testTopLevelModel.addRuleToRulePanel({name: "rule4"});

        var testTopLevel = new OverviewView({model: testTopLevelModel});

        testTopLevel.render();
        console.log(testTopLevel);


    };

    return {
        initialize: initialize
    };
});