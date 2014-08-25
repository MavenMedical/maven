/* A backbone view which displays the sources set to the rule
   a source has a name, organization which published it, and a url
 */
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'models/contextModel',
    'models/ruleModel',
    'singleRow/sourceRow',
    'text!templates/sourceManager.html',
    'text!templates/sourceRow.html',
], function ($, _, Backbone, contextModel, curRule, sourceRow, sourceManager, rowTemplate) {
 sourceManager = Backbone.View.extend({

        template: _.template(sourceManager),

        initialize: function(){

            this.$el.html(this.template())
            //if curRule has no sources, make it a new collection
            if (!curRule.get('sources')){
                curRule.set('sources', new Backbone.Collection())
            }
            //set the collection in this model to be equal to the current rule's source model
            //if the rule was new and had no sources, we just initialized it
            this.collection = curRule.get('sources');
            //if a source is added to the collection
            this.collection.on('add', function(){
                //inform the rule it needs to be saved
                            curRule.needsSave = true;
                            curRule.trigger("needsSave")
                //rerender the manager
                            this.render()
            }, this)

            //if a source is removed from the collection
            this.collection.on('remove', function(){
                //inform the rule it needs to be saved
                            curRule.needsSave = true;
                            curRule.trigger("needsSave")
                //rerender the manager
                            this.render()
            }, this)

            var panel = this;
            //if the add source button is clicked, create a new source with info from the panel and add it to the collection
            $('#add-source-button')[0].onclick = function(){
                panel.collection.add({Name: $('#source-name-field').val(), Abbreviation: $('#source-abbrev-field').val(),Hyperlink: $('#source-hyperlink-field').val()});
                //then clear the panel
                $('.source-field', this.$el).val("")

            }

            this.render()

        },
        render: function(){
                //an internal Backbone view which displays the current sources of the rule
                // params:
                //      el        :where should the div be rendered, this will be set by the Source manager to a div within it
                //      collection:what are the sources in the list, this will be the Source Manager's own model
                var listView = Backbone.View.extend({
                //its template is the source row template
                template : _.template(rowTemplate),

                initialize: function(params){
                        //the collection it will display is set here,
                        //this will be called below in the SourceManager and will be ITS collection
                        this.collection = params.collection

                        this.el = params.el
                },
                render: function(){

                    this.$el.html("");
                    var that = this
                    //for each source in the collection create a new source row and append it
                    _.each(this.collection.models, function(cur){
                        var curRow = new sourceRow({template : rowTemplate, model: cur, parent: that.collection})
                        this.$el.append(curRow.render().el)
                    }, this)

                }
            })
            //create the view of the list

            var curView = new listView({collection: this.collection, el: $('#source-list', this.$el)})
            //render it
            curView.render();

        }


    });
    return sourceManager;

});
