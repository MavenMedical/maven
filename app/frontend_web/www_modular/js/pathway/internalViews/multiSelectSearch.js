define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'pathway/internalViews/detailListBox',
    'text!templates/pathway/multiSelectSearchPanel.html'
], function ($, _, Backbone, contextModel, detailListBox, searchPanelTemplate) {

    var searchEditor = Backbone.View.extend({
        template: _.template(searchPanelTemplate),
        //function to get selected items in the right box and remove them from the model, triggering a rerender
        removeSelected: function () {
            var selected = $('.selected-items option:selected');
            _.each(selected, function (cur) {
                var id = cur.value;
                var toMove
                _.each(this.selectedBox.collection.models, function (curModel) {
                    if (cur.value == curModel.get('id')) {
                        this.selected_items.remove(curModel)
                    }
                }, this)
            }, this)
        },
        //function to get selected items in the left box and add them to the model, triggering a rerender
        addSelected: function () {
            var selected = $('.available-items option:selected');
            _.each(selected, function (cur) {
                var id = cur.value;
                var toMove
                _.each(this.availableBox.collection.models, function (curModel) {
                    if (cur.value == curModel.get('id')) {
                        this.selected_items.add(curModel)
                    }
                }, this)
            }, this)
        },
        initialize: function (params) {
            this.$el.html(this.template());
            var panel = this
            this.type = params.type;
            //availible items comes in as an empty model with a url for searching
            this.avail = params.avail;
            //selected items is the backbone model from the tree which can propagate changes to the tree
            this.selected_items = params.selected
            this.el = params.el;
            //rerender when the left box gets data from the DB, for instance when a search finishes
            this.avail.on('sync', this.render, this);
            //for all types that arent groups, add listeners to the search text field
            if (this.type != "group") {
                $('.search-button', this.$el)[0].onclick = function () {
                    //specify the parameters to send for a search on terminology
                    var t = contextModel.toParams();
                    $.extend(t, {'search_param': $('.search-input', panel.$el).val()})
                    var tp= "snomed_diagnosis"
                    if (panel.type.split('_')[1] == 'proc'){
                        tp = "CPT"
                    } else if (panel.type.split("_")[1] == 'NDC' || panel.type.split("_")[1] == 'med'){
                        tp = "snomed_drug";
                    }
                    $.extend(t, {'type': tp});
                    panel.avail.fetch({data: $.param(t)})
                }
                //do the same when you hit enter as when the search button is clicked
                $('.search-input', this.$el)[0].onkeypress = function (key) {
                    //specify the parameters to send for a search on terminology
                    if (key.keyCode == 13) {
                        var t = contextModel.toParams();
                        $.extend(t, {'search_param': $('.search-input', panel.$el).val()})
                        var tp = "snomed_diagnosis"
                        if (panel.type.split('_')[1] == 'proc'){
                        tp = "CPT"
                        } else if (panel.type.split("_")[1] == 'NDC' || panel.type.split("_")[1] == 'med'){
                            tp = "snomed_drug";
                        }
                        $.extend(t, {'type': tp});
                        panel.avail.fetch({data: $.param(t)})
                    }
                }
            } else {
                //for the user group detail type, just populate from the server right away and hide the search box
                panel.avail.fetch()
                $('.search-input').hide()
                $('.search-button').hide()
            }
            this.render()
        },
        render: function () {
            var panel = this;
            //make a new detail list box for availible items on the left
            this.availableBox = new detailListBox({items: this.avail, type: this.type, el: $('.available-items', this.$el)});
            //make a new detailListBox for currently selected items on the right
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
