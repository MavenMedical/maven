
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',
    'models/ruleModel',
    'internalViews/detailListBox',
    'text!templates/individualDetails/multiSelectSearchPanel.html'
], function ($, _, Backbone, contextModel, curRule, detailListBox, searchPanelTemplate) {

    var searchEditor = Backbone.View.extend({
        template: _.template(searchPanelTemplate),
        removeSelected: function(){
            var selected = $('.selected-items option:selected');
               _.each(selected, function(cur){
                 var id = cur.value;
                  var toMove
                  _.each(this.selectedBox.collection.models, function(curModel){
                     if(cur.value == curModel.get('id')){
                         this.selected_items.remove(curModel)
                     }
                 }, this)
              }, this)
        },
        addSelected: function(){
            var selected = $('.available-items option:selected');
            _.each(selected, function(cur){
                var id = cur.value;
                var toMove
                _.each(this.availableBox.collection.models, function(curModel){
                    if(cur.value == curModel.get('id')){
                        this.selected_items.add(curModel)
                    }
                }, this)
            }, this)
         },
         initialize: function(params){
            this.$el.html(this.template());
            var panel = this
            this.type = params.type;
            this.avail = params.avail;
            this.selected_items = new Backbone.Collection()
            this.el = params.el;
            this.avail.on('sync', this.render, this);
            $('.search-button', this.$el)[0].onclick = function(){
                var t = contextModel.toParams();
                $.extend( t, {'search_param': $('.search-input', panel.$el).val()})
                $.extend( t, {'type': panel.type});
                panel.avail.fetch({data:$.param(t)})
            }
            $('.search-input', this.$el)[0].onkeypress = function(key){
                if (key.keyCode == 13){
                    var t = contextModel.toParams();
                    $.extend( t, {'search_param': $('.search-input', panel.$el).val()})
                    $.extend( t, {'type': panel.type});
                    panel.avail.fetch({data:$.param(t)})
                }
            }
            this.render()
        },
        render: function(){
            var panel = this;
            this.availableBox = new detailListBox({items: this.avail, type: this.type, el: $('.available-items', this.$el)});
            this.selectedBox = new detailListBox({items: this.selected_items, type: this.type, el: $('.selected-items', this.$el)});
            return this;
        },
        events: {
	    "click .add-item-button": 'addSelected',
        "click .remove-item-button": 'removeSelected'

	    }
    });

    return searchEditor;

});
