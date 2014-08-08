define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/ruleModel',
    'text!templates/DecisionTree/treeNode.html',
    ], function($, _, Backbone, curRule, nodeTemplate){

        var treeNode = Backbone.View.extend({

            template: _.template(nodeTemplate),
            initialize: function(params){
                this.el = params.el
                this.$el.html(this.template({text:params.text}))
                var label
                var negLabel
                if (params.veracity){
                    label = "YES"
                    negLabel="NO"
                } else {
                    label ="NO"
                    negLabel="YES"
                }
                this.negOverlay = [["Label", {id:params.text , labelStyle:{color:"Black", fillStyle:"White"}, label:negLabel, location:.1}],["Arrow", {location: 1}]]

                this.posOverlay = [["Label", {id:params.text, labelStyle:{color:"Black", fillStyle:"White"}, label:label}], ["Arrow", {location: 1}]

                ]


                this.entryPoint =jsPlumb.addEndpoint(this.$el, {anchor:"Top"})
                this.exitPoint = jsPlumb.addEndpoint(this.$el, {anchor: "Bottom"})
                this.negativePoint = jsPlumb.addEndpoint(this.$el, {anchor:"Right"})

            }








        })
        return treeNode;

    })

