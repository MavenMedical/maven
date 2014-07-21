
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'models/contextModel',
    'models/ruleModel',
    'text!templates/ListBox.html',
    'text!templates/SearchSelectorRow/triggerSelectorRow.html'
], function ($, _, Backbone, contextModel, curRule, triggerListBox, triggerSelectorRow) {

    var TriggerEditor = Backbone.View.extend({

        template: _.template(triggerListBox),
        initialize: function(params){
            this.el = params.el
            this.collection  = params.triggers;
            this.collection.on('add', this.render, this);
            this.collection.on('remove', this.render, this)
            this.collection.on('reset', this.render, this)

            curRule.on('change:id', this.render, this)
            curRule.on('typeChange', function(){
              this.collection.reset()
            }, this)
            var that = this;
            this.$el.on('contextmenu', function(){
                that.loadParents($("option:selected", that.$el)[0].value)
            })
//           this.$el.on('dblclick', function(){
//               that.loadChildren(e)
//
//
//            })
        },
        loadChildren: function(){
            var snomed = $("option:selected", this.$el)[0].value
            var t = contextModel.toParams();
            $.extend( t, {'search_param': snomed})
            $.extend( t, {'type': "snomed_zoom_in"});
            this.collection.fetch({data:$.param(t)})

        },
        loadParents: function(){
            var snomed = $("option:selected", this.$el)[0].value
            var t = contextModel.toParams();
            $.extend( t, {'search_param': snomed})
            $.extend( t, {'type': "snomed_zoom_out"});
            this.collection.fetch({data:$.param(t)})

        },
        render: function(){
            var text = "";
            _.each(this.collection.models, function(cur){

                var entryview = Backbone.View.extend({
                    template: _.template(triggerSelectorRow),
                    render: function(){
                        if (!this.model.get('route')){
                            this.model.set("route", "")
                         }
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
