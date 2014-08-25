/* a  Backbone view for viewing the basic details about the rule and changing them,
    displays triggers, 'evidence' (Which is actually the title and description and should be renamed)
    the sex and age requirement, and whether the rule fires on drugs or procedures
 */
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',
    'models/ruleModel',
    'models/ruleCollection',
    'text!templates/ruleOverview.html',
    'text!templates/triggerSelector/triggerRow.html'

], function ($, _, Backbone, contextModel, curRule, curCollection, ruleOverviewTemplate, triggerRowTemplate) {
    //if the name of the rule is clicked prompt the user for a new name, if they enter one update the rule
    var editName = function(){
        var name = prompt("Enter The New Name");
        if (name){
            curRule.rename(name);
        }
        //the rule needs a save now
        curRule.needsSave = true;

        curRule.trigger("needsSave")
    }
    //if the min age of the rule is clicked prompt the user for a new minimum age, if they enter one update the rule
    var editMinAge = function(){
        var minAge = prompt("Enter The New Minimum Age");
        if (minAge){
            curRule.set('minAge', minAge);
        }
        curRule.needsSave = true;
        curRule.trigger("needsSave")
    }
        //if the max age of the rule is clicked prompt the user for a new minimum age, if they enter one update the rule
    var editMaxAge = function(){
        var maxAge = prompt("Enter The New Maximum Age");
        if (maxAge){
            curRule.set('maxAge', maxAge);
        }
        curRule.needsSave = true;
        curRule.trigger("needsSave")
    }
    /* UNUSED OLD INPUT TYPE
    var editGenders = function(){
        var genders = prompt("Enter The New Genders (M, F, MF)");
        if (genders){
            curRule.set('genders', genders);

        }
        curRule.needsSave = true;
        curRule.trigger("needsSave")
    }

    var editTriggerType = function(){
            var type = prompt("Enter the New Trigger Type (proc, drug) WARNING: Changing Type Will Clear All Triggers")
            if ((type == 'HCPCS' || type == 'NDC') && type!=curRule.get('type')){
                curRule.set('triggerType', type);

            }
        curRule.needsSave = true;
        curRule.trigger("needsSave")
        }
        */
    //if the user switches the type of trigger from drugs to procedures or back
    var selectorType = function(){
        //set it into the data structure
        curRule.set('triggerType', $('#trigger-type-selector').val())
        //alert the trigger list that its current triggers are invalid and need to be cleared
        curRule.trigger('typeChange')
        //inform the rule it needs to be updated in persistance
        curRule.needsSave = true;
        curRule.trigger("needsSave")

    }



    //if the user sets a new gender option in the dropdown set it into the data structure
    var selectorGenders = function(){
        curRule.set('genders', $('#gender-selector').val())
        //alert the rule it needs to be saved
        curRule.needsSave = true;
        curRule.trigger("needsSave")
    }


    var RuleOverview = Backbone.View.extend({
        template: _.template(ruleOverviewTemplate),
        //if the current rule is valid to be rendered render it and paint its triggers into it
        //otherwise hide this el
        updateOverview: function(){
            if (contextModel.get('id')) {
               this.$el.show();
               this.render();
               this.addTriggers();
            } else {
                this.$el.hide();
            }
        },
        initialize: function(){
            //if the curRule is changed in any way update the overview
            curRule.on('change', this.updateOverview, this)
            //if a trigger is addded or remove, or the entire trigger collection is reset update the overview
            curRule.get('triggers').on('add', this.updateOverview, this)
            curRule.get('triggers').on('remove', this.updateOverview, this)
            curRule.get('triggers').on('reset', this.updateOverview, this)
            //if a rule is removed from the collection, if it is the rule being displayed, hide this overview
            curCollection.on('remove', function(removed){
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
        //add the parametrized trigger to the display
        addTrigger: function(trigger){
           var triggerDisp = Backbone.View.extend({
              template: _.template(triggerRowTemplate),
              render: function(){
                  this.$el.html(this.template(this.model.attributes.toJSON()));
                  return this;
              }
           });
              var temp = new triggerDisp({model:trigger})
              $('.trigger_list', this.$el).append(temp.render().el);

        },

        //add all the triggers to display
        addTriggers: function(){
            curRule.get('triggers').each(function(cur){
                var trigger = new Backbone.Model(cur);
                this.addTrigger(trigger);
            }, this);
        },

        //all the clicks
	events: {
        "click #nameTag" : editName,
        "click #minAgeTag": editMinAge,
        "click #maxAgeTag": editMaxAge,
        "click #genderTag": editGenders,
        "click #triggerTag": editTriggerType,
        "change #gender-selector": selectorGenders,
        "change #trigger-type-selector": selectorType
	    }
    });

    return RuleOverview;

});
