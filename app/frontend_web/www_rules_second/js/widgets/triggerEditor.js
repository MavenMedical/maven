
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',
    'models/ruleModel',
    'internalViews/triggerListBox',
    'internalViews/routeListBox',

    'text!templates/triggerSelector/triggerSelectorPanel.html'
], function ($, _, Backbone, contextModel, curRule, TriggerListBox, routeListBox,  ruleListTemplate) {

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
           curRule.needsSave = true;
           curRule.trigger("needsSave")
    };

    var TriggerEditor = Backbone.View.extend({
    addSelected: function(){
        var selected = $('.available-triggers option:selected');
        _.each(selected, function(cur){
            var id = cur.value;
            var toMove
            _.each(this.availableBox.collection.models, function(curModel){
                if(cur.value == curModel.get('id')){
                    var otherModel = new Backbone.Model(curModel.attributes)
                    if (curRule.get("triggerType")=="NDC"){
                        otherModel.set("route", $('.entries', this.$el).val())
                        otherModel.set("id", curModel.get('id') + otherModel.get('route'))
                    }
                    curRule.get('triggers').add(otherModel);
                }
            }, this)
        }, this)
        curRule.needsSave = true;
        curRule.trigger("needsSave")
    },
        keyDownSearch: function(key){
            if (key.keyCode == 13)
                this.populateBySearch()
        },
        populateBySearch: function(){

            var t = contextModel.toParams();
            $.extend( t, {'search_param': $('#triggerSearch').val()})
            if (curRule.get('triggerType')=='NDC')
                $.extend( t, {'type': "snomed_drug"})
            else
                $.extend( t, {'type': "CPT"})
            this.availModel.fetch({data:$.param(t)})
        },
        loadAvailChildren: function(){
            this.availableBox.loadChildren()
        },
        loadAvailParents: function(){
            this.availableBox.loadParents()
        },


        template: _.template(ruleListTemplate),
        initialize: function(){
              this.$el.html(this.template());
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
            }, this)
             this.routeBox = new routeListBox({el: $('.route-list',  this.el)});
            curRule.on('change:triggerType', function(){
                if (curRule.get('triggerType')=='NDC'){
                     this.routeBox.$el.show()
                } else {
                     this.routeBox.$el.hide()
                 }
            }, this)
            this.$el.hide()
            this.render()

        },

        render: function(){
            var panel = this;

            if (curRule.get('triggerType')=='NDC')
                this.routeBox.$el.show();
            else
                if (this.routeBox.$el.hide())
            availEl = $('.available-triggers', this.$el)
            this.availableBox = new TriggerListBox({triggers: this.availModel, el: availEl});
            this.availableBox.render()
            selectedEl = $('.selected-triggers', this.$el)
            this.selectedBox = new TriggerListBox({triggers: curRule.get('triggers'), el: selectedEl});
            this.selectedBox.render()



            return this;
        },
        events: {
            "click #addTriggerButton" : 'addSelected',
            "click #removeTriggerButton" : removeSelected,
            "click #searchTriggers" : 'populateBySearch',
            "keypress #triggerSearch": 'keyDownSearch',
            "dblclick .available-triggers": 'addSelected',
            "click #zoom-in-button": 'loadAvailChildren',
            "click #zoom-out-button": "loadAvailParents"
	    }
    });

    return TriggerEditor;

});
