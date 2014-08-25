
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

   'globalmodels/contextModel',
    'text!templates/pathway/ListBox.html',
    'text!templates/pathway/resultRow.html'
], function ($, _, Backbone, contextModel, triggerListBox, lineTemplate) {

    var detailListBox = Backbone.View.extend({

        template: _.template(triggerListBox),
        initialize: function(params){
            var panel = this
            this.collection  = params.items;

            this.type = params.type;
            this.$el = params.el

            panel.lineTemplate = _.template(lineTemplate)
            panel.collection.on('add', panel.render, panel);
            panel.collection.on('remove', panel.render, panel)

            panel.render()



        },

        render: function(){

            var text = "";
            var panel = this
            _.each(this.collection.models, function(cur){

                var entryview = Backbone.View.extend({
                        render: function(){
                            this.$el.html(panel.lineTemplate(this.model.toJSON()));
                            return this;
                    }
                });
                var curentry = new entryview({model: cur});
                text+= (curentry.render().el.innerHTML);
            }, this);
            this.$el.html(this.template({listEntries:text}));
            return this;
        }

    });
    return detailListBox;

});
