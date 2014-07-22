define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',
    'models/ruleModel',

    'Helpers',
    'text!templates/DecisionTree/treeTemplate.html',
    'text!templates/DecisionTree/treeNode.html',
     ],

    function($, _, Backbone, contextModel, curRule, Helpers, treeTemplate, treeNodeTemplate){




        var TreeView = Backbone.View.extend({
            template: _.template(treeTemplate),
            initialize: function(){


            },
            render: function(){




            },
            renderOff: function(curDetail, curNode){


            }



        })


















        return TreeView
    });






