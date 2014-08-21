/*
    similar to the detail list box but interfaces with curRule.triggers
    params:
        triggers    : passed from the widget which renders this view, the initial list of triggers contained in the list
        el          : the loacation at which to render the list box

 */
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
            // if a new rule is selected rerender this panel
            curRule.on('change:id', this.render, this)
            // if the rule is changed from drugs to procedures (directly through the rule overview not by changing rules)
            // clear the list box as all the current entries are invalid
            curRule.on('typeChange', function(){
              this.collection.reset()
            }, this)
            var that = this;
            //zoom the snomed concept out on right click
            this.$el.on('contextmenu', function(){
                that.loadParents($("option:selected", that.$el)[0].value)
            })
//           this.$el.on('dblclick', function(){
//               that.loadChildren(e)
//
//
//            })
        },
        //change the contents of the list to be equal to the direct snomed children of the currently selected item
        loadChildren: function(){
            var snomed = $("option:selected", this.$el)[0].value
            var t = contextModel.toParams();
            $.extend( t, {'search_param': snomed})
            $.extend( t, {'type': "snomed_zoom_in"});
            this.collection.fetch({data:$.param(t)})

        },
        //change the contents of the list to be equal to the direct snomed parents of the currently selected item
        loadParents: function(){
            var snomed = $("option:selected", this.$el)[0].value
            var t = contextModel.toParams();
            $.extend( t, {'search_param': snomed})
            $.extend( t, {'type': "snomed_zoom_out"});
            this.collection.fetch({data:$.param(t)})

        },
        render: function(){
            var text = "";
            //for each item in the collection, render the row
            _.each(this.collection.models, function(cur){


                //a backbone view displaying a row of the collection
                var entryview = Backbone.View.extend({
                    template: _.template(triggerSelectorRow),
                    render: function(){
                        //if the model being rendered has no route, the route is the empty string not undefined
                        if (!this.model.get('route')){
                            this.model.set("route", "")
                         }

                        this.$el.html(this.template(this.model.toJSON()));
                        return this;

                    }
                });

                var curentry = new entryview({model: cur});
                //accumulate the text to be rendered in the box
                text+= (curentry.render().el.innerHTML);
            }, this);
            //set the div to contain the requisite text

            this.$el.html(this.template({listEntries:text}));
            return this;
        }

    });
    return TriggerEditor;

});
