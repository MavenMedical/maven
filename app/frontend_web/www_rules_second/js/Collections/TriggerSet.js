define([
    'jquery',
    'underscore',
    'backbone',
    'Models/Trigger',
    
], function($, _, Backbone, Trigger) {
    
    var TriggerSet = Backbone.Collection.extend({
        model: Trigger,

        initialize: function(params){
           this.type = params.type;


        },
        addTrigger: function(params){
            var toAdd = new Trigger({'type': this.type, code: params.code})
            this.add(toAdd);
        }

    });
    return TriggerSet;

});
