
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',
    'models/Rule',
    'models/ruleCollection',
    'text!templates/ruleOverview.html',
    'text!templates/triggerRow.html'

], function ($, _, Backbone, contextModel, curRule, curCollection, ruleOverviewTemplate, triggerRowTemplate) {
    var showTriggerEditor = function(){
      console.log("show the trigger editor");
    };

    
    var RuleOverview = Backbone.View.extend({
        template: _.template(ruleOverviewTemplate),
        updateOverview: function(){
               this.render();
               this.addTriggers();

        },
        initialize: function(){

            curRule.on('change:name', this.updateOverview, this)
            curRule.on('change:')
            curCollection.on('remove', function(removed){
                console.log(contextModel);

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
                  console.log(this.model.toJSON());
                  this.$el.html(this.template({type:this.model.get('type'), code:this.model.get('code')}));
                  return this;
              }
           });
            var temp = new triggerDisp({model:trigger})
              $('.trigger_list', this.$el).append(temp.render().el);

        },
        addTriggers: function(){
            for (var i in curRule.get('triggers')){
                var cur = curRule.get('triggers')[i];
                var trigger = new Backbone.Model(cur);
                this.addTrigger(trigger);
            }


        },


	events: {
	    "click #EditTriggersButton" : showTriggerEditor
	}
    });

    return RuleOverview;

});
