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

            console.log(this);
        }

    });
    return TriggerSet;

});
