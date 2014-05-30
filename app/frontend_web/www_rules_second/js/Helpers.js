define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone


], function ($, _, Backbone) {

    var Helpers = {
        detailID:0,
        triggerID:0,
        CreateRule: function(){},
        AddTrigger: function(triggerToAdd, setToAddTo){

        },
        getNewDetailID:function(){
            this.detailID ++;
            return this.detailID;


        },
        getNewTriggerID:function(){
            this.triggerID ++;
            return this.triggerID;
        }

    };

    return Helpers;


});
