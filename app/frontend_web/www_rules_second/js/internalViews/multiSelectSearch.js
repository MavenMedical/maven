/*
    backbone view for displaying a set of selection panels for choosing a set of snomed concepts, loincs, or cpt codes
    for use by details

    consists of two detailListBox objects, a search field which searches the terminology to populate the 'available' box
    on the left, and buttons copy the selected concepts in the the 'available' box to the 'selected' box on the right

    params:
        el               : the location in which to render the multi select search
        type             : the type of concepts to search for (snomed, loinc, cpt)
        avail            : the Backbone.Collection representing initial contents of the 'availible' column on the left
                           should in pretty much all cases be a new Backbone.Collection()
        selected_items   : the Backbone.Collection representing initial contents of the 'selected' column on the right
                           sent by the detail editor rendering this view, represents the initial contents of the
                           represented field for the detail being edited

 */
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

        //find the selected items in the 'selected' box and remove them from the 'selected' box
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
        //find the selected items in the 'avail' box and add them to the 'selected' box
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
            var panel = this
             //load the params, initialize the template
            this.type = params.type;
            this.avail = params.avail;
            this.selected_items = params.selected
            this.el = params.el;
            this.$el.html(this.template());
            //events:
            //  when a search to the terminology databases completes, rerender the view could possibly be moved to the individual list boxes
            this.avail.on('sync', this.render, this);

            //when you click the search button, fetch the results from the terminology into the avail box
            //in addition to the user and auth info add the parameter of the search term from the '.search-input box
            $('.search-button', this.$el)[0].onclick = function(){
                var t = contextModel.toParams();
                $.extend( t, {'search_param': $('.search-input', panel.$el).val()})
                $.extend( t, {'type': panel.type});
                panel.avail.fetch({data:$.param(t)})
            }
             //also do the search if enter is pressed
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
            //create the two list boxes
            this.availableBox = new detailListBox({items: this.avail, type: this.type, el: $('.available-items', this.$el)});
            this.selectedBox = new detailListBox({items: this.selected_items, type: this.type, el: $('.selected-items', this.$el)});
            return this;
        },
        //handlers for the two buttons
        events: {
	    "click .add-item-button": 'addSelected',
        "click .remove-item-button": 'removeSelected'

	    }
    });

    return searchEditor;

});
