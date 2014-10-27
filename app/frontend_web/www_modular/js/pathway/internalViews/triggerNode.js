define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'pathway/internalViews/treeNode',
    'text!templates/pathway/triggerNode.html'



    ], function($, _, Backbone, TreeNode, myTemplate){

        var TriggerNode = TreeNode.extend({
             nodeType: "topLevel",
             template:  _.template(myTemplate)

        })


        return TriggerNode;

    })

