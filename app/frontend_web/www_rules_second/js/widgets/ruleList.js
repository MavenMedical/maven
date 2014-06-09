
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',
    'models/ruleCollection',
    'models/ruleModel',
    'singleRow/ruleRow',
    'text!templates/ruleList.html',
    'text!templates/ruleRow.html'
], function ($, _, Backbone, contextModel, ruleCollection, curRule, RuleRow, ruleListTemplate) {




    var RuleList = Backbone.View.extend({
        initialize: function(){
            this.template = _.template(ruleListTemplate);
            ruleCollection.on('add', this.addRule, this);
            ruleCollection.on('reset', this.render, this);
            ruleCollection.on('remove', this.addAll, this);

            this.addAll();
        },
        render: function(){
	    //console.log(this.$el);
            this.$el.html(this.template({}));
            return this;
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

            })

            $('.rule-table', this.$el).append(rulerow.render().el);
        },
	addAll: function() {
	    this.render();
	    for(var pat in ruleCollection.models) {
		    this.addRule(ruleCollection.models[pat]);
	    }
	},
	events: {
	    "click #addRuleButton" : "createRule"
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
