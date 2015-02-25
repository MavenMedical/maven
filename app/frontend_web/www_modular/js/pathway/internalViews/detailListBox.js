
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

   'globalmodels/contextModel',
    'text!templates/pathway/ListBox.html',
    'text!templates/pathway/resultRow.html',
    'text!templates/pathway/groupResultRow.html',
    'text!templates/pathway/cptResultRow.html',

], function ($, _, Backbone, contextModel, triggerListBox, snomedLineTemplate, groupLineTemplate, cptLineTemplate ) {
    //this detail list box is used for the double multi select boxes for adding terminology to a detail
    //it has a collection of terminology objects and a type telling it what template to use to render them
    var detailListBox = Backbone.View.extend({

        template: _.template(triggerListBox),
        initialize: function(params){
            var panel = this
            this.collection  = params.items;

            this.type = params.type;
            this.$el = params.el

            //choose the line template based on the type controls contextual text and formatting
            if (this.type.split('_')[0] ==  "snomed"){
                panel.lineTemplate = _.template(snomedLineTemplate)
            } else if (this.type == "groups"){
                panel.lineTemplate = _.template(groupLineTemplate)
            } else if (this.type == "hist_proc"){
                panel.lineTemplate = _.template(cptLineTemplate)
            }
            panel.collection.on('add', panel.render, panel);
            panel.collection.on('remove', panel.render, panel)

            panel.render()



        },
        //loop through the collection and print the lines using the template
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

            //old way of doing things, amalgamate the text first then set all of the html to it
            //could be changed to append one line at a time, but this works
            this.$el.html(this.template({listEntries:text}));
            return this;
        }

    });
    return detailListBox;

});
