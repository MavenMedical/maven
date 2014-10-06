
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'pathway/models/treeModel',
    'pathway/modalViews/editNode',
    'pathway/modalViews/newPathway',
    'pathway/modalViews/detailEditor',
    'pathway/modalViews/nodeEditor',
    'pathway/modalViews/protocolEditor',
    'pathway/modalViews/sidePanelEditor',
    'text!templates/pathway/treeNodeActionSet.html'

], function ($, _, Backbone, contextModel, curTree, editNode, NewPathway, DetailEditor, nodeModal,protocolModal, sidePanelEditor, treeNodeActionSetTemplate) {


    var treeNodeActionSet = Backbone.View.extend({
        template: _.template(treeNodeActionSetTemplate),
        render: function(){
            var nodeType;
            if(curTree.get('selectedNode').attributes != null){
                this.$el.html(this.template(curTree.get('selectedNode').attributes))
            }
            $('#deleteNodeButton', this.$el)[0].onclick = this.deleteNode
            $('#setNodeTitleButton', this.$el)[0].onclick = this.editName

            return this;
        },


        editName: function(){
            new editNode();
           /* console.log('tree', curTree.get('selectedNode').attributes.triggers);
            var newname = prompt("Enter the new title")
            if (newname)
                curTree.get('selectedNode').set('name', newname)*/
        },




        deleteNode: function(){
            var x = true
                if (curTree.get('selectedNode').get('children').length>0)
                    x = confirm("You are about to delete this node and ALL of its children\nDo you wish to continue?")
            if (x) curTree.deleteNode(curTree.get('selectedNode'))

        }

    })

    return treeNodeActionSet

});
