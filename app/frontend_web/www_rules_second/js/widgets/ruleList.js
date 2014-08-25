/*this is a Backbone View which displays the list of available rules to be loaded into the editor
    it implements the ruleRow singleRow view
    it also houses the buttons for saving and creating rules
 */
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
            //if the rule collection recieves an additional rule add it to the list
            ruleCollection.on('add', this.addRule, this);
            //if the rule collection is cleared, rerender the list to empty
            ruleCollection.on('reset', this.render, this);
            //if a rule is removed rerender the list
            ruleCollection.on('remove', this.addAll, this);
            //if the curRule reports it needs to be saved, enable the button to save rule
            curRule.on("needsSave", function(){
                $("#saveRuleButton").attr('disabled', false)

            })
            //add all the items to thel ist when it is initialized
            this.addAll();
        },
        render: function(){

            this.$el.html(this.template({}));

            return this;
        },
        //if the save rule button is clicked write to persistance
        saveRule: function(){
            //show the saving modal
          var saveMod = new savingModal();
            //save the rule
          curRule.save({}, {success: function(){
            $("#saveRuleButton").attr('disabled', true)
            //the rule no longer needs a save
              curRule.needsSave=false;
              //hide the modal
            $("#detail-modal").modal('hide');
          }});



        },
        //add the rule in parameters to the list
	    addRule: function(rule){
            //create a new row modeling the rule
            var rulerow = new RuleRow({
                model: rule
            });
            //if the rules name is changed rerender it
            rule.on('change:name', function(){
                rulerow.render();
            }, this)
            //if the rule is destroyed remove it from the collection
            rule.on('destroy', function(){
                ruleCollection.remove(rule);
            })
            //if the rule is currently selected, make it big, this will happen when add rule is called by create rule
            //but not when it is called from a new fetch of the rule editor
            if (rule.get('id') == curRule.get('id')){
                rulerow.$el.css({'font-size': '200%'});
            } else {
                rulerow.$el.css({'font-size': '100%'});
            }

            $('.rule-table', this.$el).append(rulerow.render().el);

        },
        //call add rule for all the rules in the collection
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
