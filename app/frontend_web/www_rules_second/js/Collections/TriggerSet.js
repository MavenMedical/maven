define([
    'jquery',
    'underscore',
    'backbone',
    'Models/Trigger',
    
], function($, _, Backbone, Trigger) {
    
    var TriggerSet = Backbone.Collection.extend({
        model: Trigger,


        addTrigger: function(params){
            var toAdd = new Trigger({'type': params.type, code: params.code})
            this.add(toAdd);
        },
        getTriggerByID: function(idIn){
            var result = null;
            this.each(function(cur){
             console.log("loop1");

                if ((cur.get('id')+"")==idIn ){


                    result = cur;

                }


            }, this);
                 return result;
        }

    });
    return TriggerSet;

});
