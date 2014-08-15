/* the backbone view representing a node of the tree view, contains info about whether the

    params :
        el          : the location in which to render the node
        veracity    : does this rule need a NO branching right and a YES down or vice versa

 */
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
                //fill the node template with the correct text
                this.$el.html(this.template({text:params.text}))
                var label
                var negLabel
                //Set the label based on the varacity parameter
                if (params.veracity){
                    label = "YES"
                    negLabel="NO"
                } else {
                    label ="NO"
                    negLabel="YES"
                }
                //create the overlays
                this.negOverlay = [["Label", {id:params.text , labelStyle:{color:"Black", fillStyle:"White"}, label:negLabel, location:.1}],["Arrow", {location: 1}]]
                this.posOverlay = [["Label", {id:params.text, labelStyle:{color:"Black", fillStyle:"White"}, label:label}], ["Arrow", {location: 1}]

                ]

                //add JSPlumb endpoints to the top bottom and right of the node
                this.entryPoint =jsPlumb.addEndpoint(this.$el, {anchor:"Top"})
                this.exitPoint = jsPlumb.addEndpoint(this.$el, {anchor: "Bottom"})
                this.negativePoint = jsPlumb.addEndpoint(this.$el, {anchor:"Right"})

            }

        })
        return treeNode;

    })

