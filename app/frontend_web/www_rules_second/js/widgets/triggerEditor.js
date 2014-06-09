
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',
    'models/ruleModel',
    'internalViews/triggerListBox',

    'text!templates/triggerSelectorPanel.html'
], function ($, _, Backbone, contextModel, curRule, TriggerListBox, ruleListTemplate) {
    var addSelected = function(){

        var selected = $('.available-triggers option:selected');
        _.each(selected, function(cur){
            var id = cur.value;
            var toMove
            _.each(this.availableBox.collection.models, function(curModel){
                if(cur.value == curModel.get('id')){

                    curRule.get('triggers').add(curModel);
                }
            }, this)
        }, this)
        console.log(curRule);
        curRule.save();

    };
    var removeSelected = function(){
      var selected = $('.selected-triggers option:selected');
        _.each(selected, function(cur){
            var id = cur.value;
            var toMove
            _.each(this.selectedBox.collection.models, function(curModel){
                if(cur.value == curModel.get('id')){
                    curRule.get('triggers').remove(curModel);

                }
            }, this)
        }, this)

        curRule.save();



    };
    var TriggerEditor = Backbone.View.extend({
        template: _.template(ruleListTemplate),
        updateSelector: function(){
            contextModel.set('showTriggerEditor', false);
            this.render();

        },

        initialize: function(){
          this.$el.hide();


            var panel = this;
            var anon =  Backbone.Collection.extend( {url: '/triggers?'});
            var searchedTriggers = new anon();
            searchedTriggers.fetch({data:$.param(contextModel.toParams()), success: function(){

                panel.availModel = searchedTriggers;
                console.log(panel.availModel);}
            });

          contextModel.on('change:showTriggerEditor', function(newVal){
              if (newVal.get('showTriggerEditor')){
                  this.$el.show()
              } else {
                  this.$el.hide();
              }
          }, this)
          contextModel.on('change:id', this.updateSelector, this)

        },

        render: function(){
            var panel = this;
            this.$el.html(this.template());

            this.availableBox = new TriggerListBox({triggers: this.availModel});
            $('.available-triggers', this.$el).html(this.availableBox.render().$el);

            this.selectedBox = new TriggerListBox({triggers: curRule.get('triggers')});

            var result = this.selectedBox.render().$el;
            $('.selected-triggers', this.$el).html(result);

            return this;
        },
        events: {
	    "click #addTriggerButton" : addSelected,
        "click #removeTriggerButton" : removeSelected
	    }
    });

    return TriggerEditor;

});
