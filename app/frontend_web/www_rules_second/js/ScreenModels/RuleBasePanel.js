define([
    'jquery',
    'underscore',
    'backbone',
    'Collections/TriggerSet',
   

    'Helpers'


], function($, _, Backbone, TriggerSet,  Helpers) {

    var TopLevel = Backbone.Model.extend({
        defaults: {'TriggerList': null, 'name' : null},
        initialize: function(ruleIn){

            this.set('TriggerList', ruleIn.get('myTriggers'));
            this.set('name', ruleIn.get('myName'));


        }

    });

    return TopLevel;

});
