/*
    A backbone view displaying a list box from which multiple snomeds/cpts/loincs can be selected, for use by the detail
    editor modal

    params:
       collection: the Backbone Collection representing the objects which exist in this list box
       type      : the type (loinc/snomed/cpt) of the objects contained in the collection
       el        : the location in which to render this view
 */
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'models/contextModel',
    'text!templates/ListBox.html',
], function ($, _, Backbone, contextModel, ListBox ) {

    var detailListBox = Backbone.View.extend({

        template: _.template(ListBox),
        initialize: function(params){
            var panel = this
            //load the params into the object
            this.collection  = params.items;
            this.type = params.type;
            this.$el = params.el

            //load the correct line template for rendering an object of the type specified in the type field
            //when its loaded, render
            require(['text!templates/SearchSelectorRow/' + panel.type +"_ResultRow.html"], function(template){
                panel.lineTemplate = _.template(template)
                panel.collection.on('add', panel.render, panel);
                panel.collection.on('remove', panel.render, panel)

                panel.render()

            });

        },

        render: function(){

            var text = "";
            var panel = this

            //for each object in the collection render the line using the template which was set in the require above
            _.each(this.collection.models, function(cur){
                //a backbone view representing a line in the list box
                
                var entryview = Backbone.View.extend({
                        render: function(){
                            this.$el.html(panel.lineTemplate(this.model.toJSON()));
                            return this;
                        }
                });
                var curentry = new entryview({model: cur});
                panel.$el.append(new entryview({model: cur}))
            }, this);
            return this;
        }

    });
    return detailListBox;

});
