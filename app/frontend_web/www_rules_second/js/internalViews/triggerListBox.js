
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'models/contextModel',
    'text!templates/ListBox.html',
    'text!templates/SearchSelectorRow/triggerSelectorRow.html'
], function ($, _, Backbone, contextModel, triggerListBox, triggerSelectorRow) {

    var TriggerEditor = Backbone.View.extend({

        template: _.template(triggerListBox),
        initialize: function(params){

            this.collection  = params.triggers;
            this.collection.on('add', this.render, this);
            this.collection.on('remove', this.render, this)
            var that = this;
            this.$el.on('contextmenu', function(){
                that.loadParents($("option:selected", that.$el)[0].value)


            })
            this.$el.on('dblclick', function(){
                that.loadChildren($("option:selected", that.$el)[0].value)


            })
        },
        loadChildren: function(snomed){
            console.log(snomed)
            var t = contextModel.toParams();
            $.extend( t, {'search_param': snomed})
            $.extend( t, {'type': "snomed_zoom_in"});
            this.collection.fetch({data:$.param(t)})

        },
        loadParents: function(snomed){
            console.log(snomed)

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
