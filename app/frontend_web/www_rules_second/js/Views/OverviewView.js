define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'ScreenModels/Overview',

    'Views/RuleListDisplayView',
    'text!../Templates/Overview.html',


], function ($, _, Backbone, Overview, RuleListDisplayView, rTemplate) {

    var RuleList = Backbone.View.extend({

        el: "#TopLevelPanel",
        template: _.template(rTemplate),
        model: new Overview(),

        initialize: function(param){
            if (param.model){
                this.model =  param.model;
            }

        },
        render: function(){
            var html = this.template({});

            this.$el.html(html);
            var ruleListView = new  RuleListDisplayView({model: this.model.get('RulePanel')});

            ruleListView.render();

        }

    });


    return RuleList;


});
