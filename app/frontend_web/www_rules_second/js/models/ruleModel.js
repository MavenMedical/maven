define([
    'jquery',
    'underscore',
    'backbone',
    'models/contextModel'
], function($, _, Backbone, contextModel){
    var ruleModel;

    // the rule model's JSON representation is a map where each attribute either 
    // corresponds to a single literal (id, name) or a list of maps of literals
    // I want the object's representing each of these to be very similar,
    // so rather than let the literals just be literals, I'm wrapping them in a model.
    // Specifically an AnonLiteralModel.  The lists are wrapped in a collection0

    // This model wraps literal attributes of a rule
    var AnonLiteralModel = Backbone.Model.extend({
	initialize: function(key, value) {
	    this.toJSON = function() {
		return this.get(key);
	    };
	    this.type = key;
	    this.set("type", key);
	    this.set(key, value);
	    var that=this;
	    this.on('change', function() {ruleModel.propagate(that)}, ruleModel);
	}
    });

    var RuleModel = Backbone.Model.extend({
	url: function() {
	    return '/rule?' + decodeURIComponent($.param(contextModel.toParams()));
	},
	parse: function(response, options) {
	    // when we get a JSON back from the server, turn each of it's values into 
	    // a Collection or a AnonLiteralModel
	    var ret = {};
	    _.each(response, function(value,key) {
		var model;
		if(typeof value != 'object') {
		    model = new AnonLiteralModel(key, value);
		} else {
		    model = new Backbone.Collection({type:key});
		    model.set(value);
		    model.on('change', function() {ruleModel.propagate(model)}, ruleModel);
		}
		ret[key] = model;
	    });
	    return ret;
	},
	propagate: function(model) {
	    // propagate is like change, but UI driven, and coming from descendents
	    var type = model.get("type");
	    ruleModel.trigger("propagate:"+type, ruleModel);
	    console.log("propagating: "+type+", "+JSON.stringify(model));
	    // If users will explicitly save, delete this line and replace with a save button trigger.
	    this.save();
	},
	toJSON: function() {
	    // I customize the toJSON so that AnonLiteralModels behave properly
	    var ret = {};
	    _.each(this.attributes, function(value, key) {
		ret[key]=value.toJSON();
	    });
	    return ret;
	}
    });

    ruleModel = new RuleModel;

    // if the ruleModel's id changes (on a POST), update the contextModel with that id
    ruleModel.on('change:id', 
		 function() {
		     contextModel.set({'id':ruleModel.get('id').get('id')})
		 }, contextModel);

    // if the context model's id changes, update the ruleModel
    contextModel.on('change:id', 
		    function(cm) {
			if(cm.get('auth')) { // make sure the user is logged in
			    if(cm.get('id')) { // a rule was selected
				// don't fetch if the ruleModel already has the right id
				if(!('id' in ruleModel) || cm.get('id') != ruleModel.get('id').toJSON()) {
				    ruleModel.fetch();
				}
			    } else {
				// create a new empty rule model
				ruleModel.clear({silent:true});
				var namemodel = new AnonLiteralModel("name", "New Rule");
				ruleModel.set({name:namemodel});
			    }
			}
		    }, ruleModel);

    return ruleModel;
});
