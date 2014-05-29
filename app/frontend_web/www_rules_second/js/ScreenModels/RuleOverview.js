define([
    'jquery',
    'underscore',
    'backbone',
    'ScreenModels/TriggerBasePanel',
    'ScreenModels/NameEditor',

    'Helpers'

], function($, _, Backbone, RuleSet, Helpers) {

    var TopLevel = Backbone.Model.extend({

        defaults: {'RuleList': new RuleSet(), NameEdit}


    });



    return TopLevel;

});
