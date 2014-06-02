define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'ScreenModels/Overview',

    'Views/RuleListDisplayView',
    'Views/RuleOverviewView',
    'text!../Templates/Overview.html',


], function ($, _, Backbone, Overview, RuleListDisplayView, RuleOverviewView, rTemplate) {

    var OverviewView = Backbone.View.extend({

        el: "#TopLevelPanel",
        template: _.template(rTemplate),
       //Model Type is Overview

        initialize: function(param){
            if (param.model){
                this.model =  param.model;
            }
            this.model.on('change:RuleOverview', function(){
                this.render();
            }, this)

        },
        render: function(){
            var html = this.template({});

            this.$el.html(html);
            var ruleListView = new  RuleListDisplayView({model: this.model.get('RulePanel')});
            ruleListView.render();



           if (this.model.get('RuleOverview')){
                var temp = new RuleOverviewView({model: this.model.get('RuleOverview')});
                temp.render();
           }
        }

    });


    return OverviewView;


});
