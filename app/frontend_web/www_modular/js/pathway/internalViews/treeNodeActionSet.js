
define([
    //This file is not used with acetheme
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'pathway/models/treeModel',
    'pathway/models/treeContext',
    'pathway/modalViews/editNode',
    'pathway/modalViews/newPathway',
    'pathway/modalViews/nodeEditor',
    'pathway/modalViews/protocolEditor',
    'pathway/modalViews/DeleteDialog',

    'text!templates/pathway/treeNodeActionSet.html'

], function ($, _, Backbone, contextModel, curTree, treeContext, editNode, NewPathway, NodeEditor, ProtocolEditor,  deleteDialog, treeNodeActionSetTemplate) {


    var treeNodeActionSet = Backbone.View.extend({
        template: _.template(treeNodeActionSetTemplate),
        render: function(){

            var nodeType;
            if(treeContext.get('selectedNode').attributes != null){
		var selected = treeContext.get('selectedNode')
                this.$el.html(this.template({treeNode: selected.attributes, childrenHidden: selected.childrenHidden && selected.childrenHidden(), page: contextModel.get('page')}))
            }
            $('#deleteNodeButton', this.$el)[0].onclick = this.deleteNode
            $('#setNodeTitleButton', this.$el)[0].onclick = this.editNode


            var addChildButton = $('#addChildButton', this.$el)
	    if (addChildButton.length) {addChildButton[0].onclick = this.addChild}
            var protocolButton = $('#addProtocolButton', this.$el)[0]
            if(protocolButton){
                protocolButton.onclick = this.addProtocol
            }
            var collapseButton = $('#collapseButton', this.$el)[0]
            if (collapseButton){
                collapseButton.onclick = this.expandCollapse
            }
            return this;
        },
        addChild : function(){

            var newEditor = new NodeEditor(treeContext.get('selectedNode'))
        },
        addProtocol: function(){
            var newEditor = new ProtocolEditor(treeContext.get('selectedNode'))
        },
        expandCollapse: function(){
                           if (!treeContext.get('selectedNode').childrenHidden()){
                               curTree.collapse(treeContext.get('selectedNode'))
                           } else{
                               treeContext.get('selectedNode').showChildren()
                           }
            curTree.getShareCode()
            treeContext.trigger('propagate')
        },

        editNode: function(){
            new editNode();

        },

        deleteNode: function(){
            var x = true
            new deleteDialog()


        }

    })

    return treeNodeActionSet

});
