
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
   'globalmodels/contextModel',
    'pathway/models/treeModel',
    'text!templates/pathway/treeNodeActionSet.html'

], function ($, _, Backbone, contextModel, curTree, treeNodeActionSetTemplate) {


    var treeNodeActionSet = Backbone.View.extend({
        template: _.template(treeNodeActionSetTemplate),
        initialize: function(){
            curTree.on('change:name', this.render,this)
        },
        render: function(){
            this.$el.html(this.template(curTree.get('selectedNode').attributes))
            return this;
        },

        events: {
            'click #setNodeTitleButton' : 'editName',
            'click #setNodeDescriptionButton': 'editDescription',
            'click #deleteNodeButton': 'deleteNode'

        },

        editName: function(){
            var newname = prompt("Enter the new title")
            curTree.get('selectedNode').set('name', newname)
            curTree.get('selectedNode').set('text', newname)
        },

        editDescription: function(){
            var newdesc = prompt("Enter the new description")
            curTree.get('selectedNode').set('tooltip', newdesc)
        },

        editHelpText: function (){
            var newht = prompt("Enter the new description")
            curTree.get('selectedNode').set('sidePanel', newht)
        },
        deleteNode: function(){
            curTree.deleteNode(curTree.get('selectedNode'))

        }

    })

    return treeNodeActionSet

});
