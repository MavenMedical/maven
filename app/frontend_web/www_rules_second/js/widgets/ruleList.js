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
    
    var RuleList = Backbone.View.extend({
        initialize: function(){
            this.template = _.template(ruleListTemplate);
            ruleCollection.on('add', this.addRule, this);
            ruleCollection.on('reset', this.render, this);
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
            $('.table').append(rulerow.render().el);
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
	    contextModel.set({id:''})
	}
    });

    return RuleList;

});
