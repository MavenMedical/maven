
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',
    'models/treeModel',
    'text!/templates/treeNodeActionSet.html'

], function ($, _, Backbone, contextModel, curTree, treeNodeActionSetTemplate) {


    var treeNodeActionSet = Backbone.View.extend({
        template: _.template(treeNodeActionSetTemplate),
        initialize: function(){
            curTree.on('change:name', this.render,this)
        },
        render: function(){
            this.$el.html(this.template(contextModel.get('selectedNode').attributes))
            return this;
        },

        events: {
            'click #setNodeTitleButton' : 'editName',
            'click #setNodeDescriptionButton': 'editDescription',
            'click #deleteNodeButton': 'deleteNode'

        },

        editName: function(){
            var newname = prompt("Enter the new title")
            contextModel.get('selectedNode').set('name', newname)
            contextModel.get('selectedNode').set('text', newname)
            console.log(contextModel)
        },

        editDescription: function(){
            var newdesc = prompt("Enter the new description")
            contextModel.get('selectedNode').set('description', newdesc)
        },

        editHelpText: function (){
            var newht = prompt("Enter the new description")
            contextModel.get('selectedNode').set('helpText', newht)
        },
        deleteNode: function(){
            curTree.deleteNode(contextModel.get('selectedNode'))

        }

    })

    return treeNodeActionSet

});
