
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'models/contextModel',
    'models/ruleModel',
    'text!templates/sourceManager.html',
    'text!templates/sourceRow.html',
], function ($, _, Backbone, contextModel, curRule, sourceManager, rowTemplate) {
 sourceManager = Backbone.View.extend({

        template: _.template(sourceManager),

        initialize: function(){
            this.$el.html(this.template())
            this.collection = curRule.get('sources');
                        this.collection.on('add', this.render,this)
                 //       this.collection.on('add', function(){curRule.save()}, this)
                        this.collection.on('remove', this.render, this)
                 //       this.collection.on('remove', function(){curRule.save()}, this)
            var panel = this;

            $('#add-source-button')[0].onclick = function(){
                var toAdd = new Backbone.Model({Name: $('#source-name-field').val(),Abbreviation: $('#source-abbrev-field').val(),Hyperlink: $('#source-hyperlink-field').val()})
                panel.collection.add(toAdd);
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
                    _.each(this.collection.models, function(cur){
                        console.log('cur', cur)
                        this.$el.append(this.template(cur.attributes))
                        var that = this

                        $(".remove-button", this.$el).last()[0].onclick = function(){
                            console.log("cur", cur)
                            console.log(that.collection)
                            that.collection.remove(cur)

                        }
                        console.log(this.$el);
                    }, this)

                }
            })


            var curView = new listView({collection: this.collection, el: $('#source-list', this.$el)})
            curView.render();
            curRule.save();

        }


    });
    return sourceManager;

});
