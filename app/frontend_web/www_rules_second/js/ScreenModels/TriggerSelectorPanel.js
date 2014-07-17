define([
    'jquery',
    'underscore',
    'backbone',
    'Collections/TriggerSet',


    'Helpers'


], function($, _, Backbone, TriggerSet,  Helpers) {

    var TopLevel = Backbone.Model.extend({
        defaults: {'SelectedTriggerSet': null, 'AvailableTriggerSet' : null},
        initialize: function(ruleIn){

            this.set('SelectedTriggerSet', ruleIn.get('myTriggers'));
            var testTriggerSet = new TriggerSet();
            testTriggerSet.addTrigger({code: 100000, type: "procedure"});
            testTriggerSet.addTrigger({code: 200000, type: "procedure"});
            testTriggerSet.addTrigger({code: 13, type: "drug"})
            this.set('AvailableTriggerSet', testTriggerSet);




        }



    });



    return TopLevel;

});
