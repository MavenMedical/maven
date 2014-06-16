
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',
    'models/ruleModel',
    'models/ruleCollection',
    'text!templates/ruleOverview.html',
    'text!templates/triggerSelector/triggerRow.html'

], function ($, _, Backbone, contextModel, curRule, curCollection, ruleOverviewTemplate, triggerRowTemplate) {
    var showTriggerEditor = function(){
        contextModel.set({showTriggerEditor: !contextModel.get('showTriggerEditor')});
        if (contextModel.get('showTriggerEditor')){
            $("#EditTriggersButton").html("Hide Trigger Editor");
        } else {
            $("#EditTriggersButton").html("Edit Triggers");
        }
    };
    var editName = function(){
        var name = prompt("Enter The New Name");
        if (name){
            curRule.rename(name);
            curRule.save();
        }
    }
    var RuleOverview = Backbone.View.extend({
        template: _.template(ruleOverviewTemplate),
        updateOverview: function(){
            if (contextModel.get('id')) {
               this.$el.show();
               this.render();
               this.addTriggers();
            } else {
                this.$el.hide();
            }
        },
        initialize: function(){
            curRule.on('change:id', this.updateOverview, this)
            curRule.on('change:name', this.updateOverview, this)
            curRule.get('triggers').on('add', this.updateOverview, this)
            curRule.get('triggers').on('remove', this.updateOverview, this)
            curCollection.on('remove', function(removed){
                if (removed.get('id') == contextModel.get('id')){
                    curRule.set('name', null);
                    this.$el.hide();
                }
            }, this)
        },
        render: function(){
            if (curRule.get('name')){
                this.$el.show();
                this.$el.html(this.template(curRule.toJSON()));
            }
            else{
                this.$el.hide();
            }
            return this;
        },
        addTrigger: function(trigger){
           var triggerDisp = Backbone.View.extend({
              template: _.template(triggerRowTemplate),
              render: function(){
                  this.$el.html(this.template(this.model.attributes.toJSON()));
                  return this;
              }
           });
              var temp = new triggerDisp({model:trigger})
              $('.trigger_list', this.$el).append(temp.render().el);

        },
        addTriggers: function(){
            curRule.get('triggers').each(function(cur){
                var trigger = new Backbone.Model(cur);
                this.addTrigger(trigger);
            }, this);
        },
	events: {
	    "click #EditTriggersButton" : showTriggerEditor,
        "click #nameTag" : editName
	}
    });

    return RuleOverview;

});
