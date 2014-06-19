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

    /*
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
    */
    var RuleModel = Backbone.Model.extend({
	url: function() {
	    return '/rule?' + decodeURIComponent($.param(contextModel.toParams()));
	},

    rename: function(name){
        this.set('name', name);


    },
    clearData: function(){
      var trig_temp = ruleModel.get('triggers');

      ruleModel.clear({silent:true});
      trig_temp.set([], {silent:true});
      contextModel.set('showTriggerEditor', false);
      ruleModel.set('triggers', trig_temp);
      ruleModel.set({triggerType: 'proc', genders:'MF', minAge:'0', maxAge:'200'}, {silent:true});



    },
    getNewRule: function(name){
      var trig_temp = ruleModel.get('triggers');
      trig_temp.set([], {silent:true});
      ruleModel.clear({silent:true});
      ruleModel.set({name:name}, {silent:true});
      ruleModel.set('triggers', trig_temp);
      ruleModel.set({triggerType: 'proc', genders:'MF', minAge:'0', maxAge:'200'}, {silent:true});

      ruleModel.save();

    },

	parse: function(response, options) {
	    // when we get a JSON back from the server, turn each of it's values into 
	    // a Collection or a AnonLiteralModel
	    var ret = {};
	    _.each(response, function(value,key) {
		var model;
		if(typeof value != 'object') {
		    ret[key] =  value;
		} else {
            if (ruleModel.get(key)){
		        model = ruleModel.get(key);
            } else {
                model = new Backbone.Collection();
            }
            model.on('change', function() {ruleModel.propagate(model)}, ruleModel);
		    model.set(value)
            ret[key] = model;

        }
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
	}
    /*
	toJSON: function() {
	    // I customize the toJSON so that AnonLiteralModels behave properly
	    var ret = {};
	    _.each(this.attributes, function(value, key) {
		ret[key]=value.toJSON();
	    });
	    return ret;
	}
	*/
    });

    ruleModel = new RuleModel;
    ruleModel.set('triggers', new Backbone.Collection);
   ruleModel.set({triggerType: 'proc', genders:'MF', minAge:'0', maxAge:'200'}, {silent:true});

    // if the ruleModel's id changes (on a POST), update the contextModel with that id
    ruleModel.on('change:triggerType', function(){

        ruleModel.get('triggers').set([]);
        ruleModel.save();

    })
    ruleModel.on('change:id',
		 function() {
		     contextModel.set({'id':ruleModel.get('id')})
             if (ruleModel.get('id')){
                 contextModel.set('showDetails', true);
             } else {
                 contextModel.set('showDetails', false)
             }
		 }, contextModel);

    // if the context model's id changes, update the ruleModel
    contextModel.on('change:id', 
		    function(cm) {
			if(cm.get('auth')) { // make sure the user is logged in
					// don't fetch if the ruleModel already has the right id
             if (contextModel.get('id')){
				if(!('id' in ruleModel) || cm.get('id') != ruleModel.get('id')) {
                    ruleModel.clearData();
				    ruleModel.fetch();

                }
             }

			}
		    }, ruleModel);

    return ruleModel;
});
