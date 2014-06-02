define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'ScreenModels/RuleOverview',
    'ScreenModels/TriggerSelectorPanel',
    'Views/RuleEditTopView',
    'Views/TriggerSelectorView'

], function ($, _, Backbone, RuleOverview, TriggerSelectorPanel, RuleEditTopView, TriggerSelectorView) {

    var RuleOverviewView = Backbone.View.extend({

        el: "#OverviewRuleEdit",
        // Model is Type: RuleOverview(),

        initialize: function(){
               this.model.on('change:curRule', function(){
                   this.model.set('TriggerSelectorPanel', null);
                   this.render();
                }, this);
                this.model.on('change:TriggerSelectorPanel', function(){
                    this.render();

                }, this);
        },
        render: function(){
            var that = this;
            var ruleEditTopView = new RuleEditTopView({model: this.model.get('curRule')});
            ruleEditTopView.on('openEdit', function(){

                that.model.set('TriggerSelectorPanel',  new TriggerSelectorPanel(that.model.get('curRule')));
                that.render();

            });
            ruleEditTopView.render();
             if (this.model.get('TriggerSelectorPanel')){
                  var triggerSelectorView = new TriggerSelectorView({model: this.model.get('TriggerSelectorPanel')});
                    triggerSelectorView.render();
            } else {

                $("#OverviewRuleEditTriggers").html("");
            }
        }

    });


    return RuleOverviewView;


});
