
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',
    'models/ruleModel',
    'internalViews/triggerListBox',

    'text!templates/triggerSelector/triggerSelectorPanel.html'
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
        keyDownSearch: function(key){
            if (key.keyCode == 13)
                this.populateBySearch()
        },
        populateBySearch: function(){

            var t = contextModel.toParams();
            $.extend( t, {'search_param': $('#triggerSearch').val()})
            if (curRule.get('triggerType')=='drug')
                $.extend( t, {'type': "snomed_drug"})
            else
                $.extend( t, {'type': "CPT"})
            this.availModel.fetch({data:$.param(t)})
        },




        template: _.template(ruleListTemplate),
        initialize: function(){
            var panel = this;
            var anon =  Backbone.Collection.extend( {url: '/triggers?'});
            panel.availModel = new anon;
            curRule.on('cleared', function(){
                this.$el.hide()
                this.availModel.reset();
            }, this)
            curRule.on('selected', function(){
                this.$el.show();
                this.availModel.reset();
                this.render();
            }, this)
            curRule.on('change:triggerType', function(){
                this.availModel.reset();
            }, this)

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
        "click #removeTriggerButton" : removeSelected,
        "click #searchTriggers" : 'populateBySearch',
        "keypress #triggerSearch": 'keyDownSearch'

	    }
    });

    return TriggerEditor;

});
