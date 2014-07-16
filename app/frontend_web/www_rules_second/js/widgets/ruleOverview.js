
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
    var editName = function(){
        var name = prompt("Enter The New Name");
        if (name){
            curRule.rename(name);
        }
        curRule.needsSave = true;
        curRule.trigger("needsSave")
    }
    var editMinAge = function(){
        var minAge = prompt("Enter The New Minimum Age");
        if (minAge){
            curRule.set('minAge', minAge);
        }
        curRule.needsSave = true;
        curRule.trigger("needsSave")
    }
    var editMaxAge = function(){
        var maxAge = prompt("Enter The New Maximum Age");
        if (maxAge){
            curRule.set('maxAge', maxAge);
        }
        curRule.needsSave = true;
        curRule.trigger("needsSave")
    }
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
    var selectorType = function(){
        curRule.set('triggerType', $('#trigger-type-selector').val())
        curRule.trigger('typeChange')
        curRule.needsSave = true;
        curRule.trigger("needsSave")

    }

    var selectorGenders = function(){
        curRule.set('genders', $('#gender-selector').val())
        curRule.needsSave = true;
        curRule.trigger("needsSave")
    }
    var RuleOverview = Backbone.View.extend({
        template: _.template(ruleOverviewTemplate),
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
            curRule.on('change', this.updateOverview, this)
            curRule.get('triggers').on('add', this.updateOverview, this)
            curRule.get('triggers').on('remove', this.updateOverview, this)
            curRule.get('triggers').on('reset', this.updateOverview, this)
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
        addTriggers: function(){
            curRule.get('triggers').each(function(cur){
                var trigger = new Backbone.Model(cur);
                this.addTrigger(trigger);
            }, this);
        },
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
