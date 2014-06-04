
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',
    'models/ruleCollection',
    'singleRow/ruleRow',
    'text!templates/ruleList.html',
    'text!templates/ruleRow.html'
], function ($, _, Backbone, contextModel, ruleCollection, RuleRow, ruleListTemplate) {

    var createRule = function() {
	     var NewRule = Backbone.Model.extend({url: '/rule'});
         var newRule = new NewRule({name:'default'});
         ruleCollection.add(newRule);

    }
    
    var RuleList = Backbone.View.extend({
        template: _.template(ruleListTemplate),
        initialize: function(){
            ruleCollection.on('add', this.addRule, this);
            ruleCollection.on('reset', this.render, this);
            ruleCollection.on('remove', this.addAll, this);
            contextModel.on('change', this.addAll, this);
            this.addAll();
        },
        render: function(){

            this.$el.html(this.template({}));
            return this;
        },
	addRule: function(rule){
            var rulerow = new RuleRow({
                model: rule
            });
	     console.log('adding rule to list');

            $('.rule-table', this.$el).append(rulerow.render().el);
        },
	addAll: function() {
	    console.log('in addAll');
	    this.render();
	    for(var pat in ruleCollection.models) {
		    this.addRule(ruleCollection.models[pat]);
	    }
	},
	events: {
	    "click #addRuleButton" : createRule
	}
    });

    return RuleList;

});
