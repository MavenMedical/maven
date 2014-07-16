
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',
    'models/ruleCollection',
    'models/ruleModel',
    'singleRow/ruleRow',
    'modalViews/savingModal',
    'text!templates/ruleList.html',
], function ($, _, Backbone, contextModel, ruleCollection, curRule, RuleRow, savingModal, ruleListTemplate) {




    var RuleList = Backbone.View.extend({

        initialize: function(){
            this.template = _.template(ruleListTemplate);
            ruleCollection.on('add', this.addRule, this);
            ruleCollection.on('reset', this.render, this);
            ruleCollection.on('remove', this.addAll, this);
            curRule.on("needsSave", function(){
                $("#saveRuleButton").attr('disabled', false)

            })
            this.addAll();
        },
        render: function(){

            this.$el.html(this.template({}));
            return this;
        },
        saveRule: function(){
          var saveMod = new savingModal();
          curRule.save({}, {success: function(){
            $("#saveRuleButton").attr('disabled', true)
            curRule.needsSave=false;
            $("#detail-modal").modal('hide');
          }});



        },

	    addRule: function(rule){
            var rulerow = new RuleRow({
                model: rule
            });
            rule.on('change:name', function(){
                rulerow.render();
            }, this)
            rule.on('destroy', function(){
                ruleCollection.remove(rule);
                rulerow.destroy()
            })
            console.log('painting', rule, "current rule is", curRule.get('id') )
            if (rule.get('id') == curRule.get('id')){
                rulerow.$el.css({'font-size': '200%'});
            } else {
                rulerow.$el.css({'font-size': '100%'});
            }

            $('.rule-table', this.$el).append(rulerow.render().el);
        },
	addAll: function() {
	    this.render();
	    for(var pat in ruleCollection.models) {
		    this.addRule(ruleCollection.models[pat]);
	    }
	},
	events: {
	    "click #addRuleButton" : "createRule",
        "click #saveRuleButton": "saveRule"

	},
	createRule: function() {

         var name = prompt('Enter the new name for the rule');
               if (name){
                   curRule.getNewRule(name);
               }
	}
    });

    return RuleList;

});
