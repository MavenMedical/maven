define([
    'jquery',
    'underscore',
    'backbone',
    'Collections/TriggerSet',
   

    'Helpers'


], function($, _, Backbone, TriggerSet,  Helpers) {

    var TopLevel = Backbone.Model.extend({
        defaults: {'Rule': null},
        initialize: function(ruleIn){

            this.set('Rule', ruleIn);

        }

    });

    return TopLevel;

});
