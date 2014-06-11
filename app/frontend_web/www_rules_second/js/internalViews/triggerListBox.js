
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone


    'text!templates/triggerSelector/triggerListBox.html',
    'text!templates/triggerSelector/triggerSelectorRow.html'
], function ($, _, Backbone, triggerListBox, triggerSelectorRow) {
    var TriggerEditor = Backbone.View.extend({
        template: _.template(triggerListBox),
        initialize: function(params){

            this.collection  = params.triggers;
            this.collection.on('add', this.render, this);
            this.collection.on('remove', this.render, this)
        },
        render: function(){

            var text = "";
            _.each(this.collection.models, function(cur){

                var entryview = Backbone.View.extend({
                    template: _.template(triggerSelectorRow),
                    render: function(){

                        this.$el.html(this.template(this.model.toJSON()));
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

    return TriggerEditor;

});
