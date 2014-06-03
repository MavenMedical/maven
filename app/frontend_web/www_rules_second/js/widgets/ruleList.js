/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

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
	console.log('create rule here');
    }
    
    var RuleList = Backbone.View.extend({
        template: _.template(ruleListTemplate),
        initialize: function(){
            ruleCollection.on('add', this.addRule, this);
            ruleCollection.on('reset', this.render, this);
            contextModel.on('change', this.addAll, this);
            this.addAll();
        },
        render: function(){
	    //console.log(this.$el);
            this.$el.html(template({}));
            return this;
        },
	addRule: function(rule){
            var rulerow = new RuleRow({
                model: rule
            });
	    console.log('adding rule to list');
            $('.table').append(rulerow.render().el);
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
