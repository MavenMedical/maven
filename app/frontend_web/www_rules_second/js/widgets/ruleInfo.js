define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',
    'models/ruleModel',
    'text!templates/ruleInfo.html'
], function ($, _, Backbone, contextModel, ruleModel, ruleInfoTemplate) {

    var RuleInfo = Backbone.View.extend({
        initialize: function(){
            this.template = _.template(ruleInfoTemplate);
            ruleModel.on('change:name', this.setModel, this);
        },
	setModel: function() {
	    var newmodel = ruleModel.get('name');
	    if(newmodel != this.model && newmodel != null) {
		this.model=newmodel;
		newmodel.on('change:name', this.render, this);
		this.render();
	    }
	},
        render: function() {
	    this.$el.html(this.template({name:this.model.get('name'), edit:false}));
            return this;
        },
	events: {
	    "change input.rule-name-edit" : "updateName",
	    "click .rule-name-display": "editName",
	},
	updateName: function(evt) {
	    this.model.set("name",evt.currentTarget.value);
	},
	editName: function() {
	    this.$el.html(this.template({name:this.model.get('name'), edit:true}));
	    $(".rule-name-edit", this.$el).focus();
	}
    });

    return RuleInfo;

});
