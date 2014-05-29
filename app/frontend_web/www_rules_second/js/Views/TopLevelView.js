define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'Collections/RuleSet',
    'text!../Templates/OverviewRuleList.html',
    'text!../Templates/ListEntry.html'

], function ($, _, Backbone, RuleSet, rTemplate) {

    var RuleList = Backbone.View.extend({

        el: "#topLevelPanel",
        template: _.template(rTemplate),
        render: function(){
            var listText = "";
            this.collection.each(function(cur){



            }, this);
        }

    });


    return RuleList;


});
