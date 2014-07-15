
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

            this.collection = curRule.get('sources');
                        this.collection.on('add', function(){
                            curRule.needsSave = true;
                            curRule.trigger("needsSave")
                            this.render()
                        }, this)
                        this.collection.on('remove', function(){
                            curRule.needsSave = true;
                            curRule.trigger("needsSave")
                            this.render()
                        }, this)

            var panel = this;
            $('#add-source-button')[0].onclick = function(){
                panel.collection.add({Name: $('#source-name-field').val(), Abbreviation: $('#source-abbrev-field').val(),Hyperlink: $('#source-hyperlink-field').val()});
                $('.source-field', this.$el).val("")

            }
            this.render()

        },
        render: function(){
                var listView = Backbone.View.extend({

                template : _.template(rowTemplate),

                initialize: function(params){
                        this.collection = params.collection

                        this.el = params.el
                },
                render: function(){

                    this.$el.html("");
                    var that = this
                    _.each(this.collection.models, function(cur){
                        var curRow = new sourceRow({template : rowTemplate, model: cur, parent: that.collection})
                        this.$el.append(curRow.render().el)
                    }, this)

                }
            })


            var curView = new listView({collection: this.collection, el: $('#source-list', this.$el)})
            curView.render();

        }


    });
    return sourceManager;

});
