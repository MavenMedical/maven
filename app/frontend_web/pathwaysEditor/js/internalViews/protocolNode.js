define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'text!templates/protocolNode.html',

    ], function($, _, Backbone,nodeTemplate){

        var treeNode = Backbone.View.extend({

            template: _.template(nodeTemplate),
            initialize: function(params){
                this.model = params.model
                this.$el.css({'float':'left'})


            },
            makeExit: function(){

                var exit = jsPlumb.addEndpoint(this.$el, {anchor: 'Bottom'})
                return exit
            },
            makeEntrance: function(){

                var entrance = jsPlumb.addEndpoint(this.$el, {anchor: 'Top'})
                return entrance
            },
            render: function(){
                if (this.model.get('protocol').attributes){
                    this.$el.html(this.template(this.model.get('protocol').attributes))
                } else  {
                    this.$el.html(this.template(this.model.get('protocol')))
                }

                return this
            },

            treeToJSON: function(node){

            }





        })
        return treeNode;

    })

