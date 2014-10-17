
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
    'pathway/modalViews/nodeEditor',
    'pathway/modalViews/protocolEditor',
    'pathway/modalViews/DeleteDialog',

    'text!templates/pathway/treeNodeActionSet.html'

], function ($, _, Backbone, contextModel, curTree, editNode, NewPathway, DetailEditor, nodeModal,protocolModal, sidePanelEditor, NodeEditor, ProtocolEditor,  deleteDialog, treeNodeActionSetTemplate) {


    var treeNodeActionSet = Backbone.View.extend({
        template: _.template(treeNodeActionSetTemplate),
        render: function(){
            var nodeType;
            if(curTree.get('selectedNode').attributes != null){
                this.$el.html(this.template({treeNode :curTree.get('selectedNode').attributes, page: contextModel.get('page')}))
            }
            $('#deleteNodeButton', this.$el)[0].onclick = this.deleteNode
            $('#setNodeTitleButton', this.$el)[0].onclick = this.editNode
            $('#addChildButton', this.$el)[0].onclick = this.addChild
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

            var newEditor = new NodeEditor(curTree.get('selectedNode'))
        },
        addProtocol: function(){
            var newEditor = new ProtocolEditor(curTree.get('selectedNode'))
        },
        expandCollapse: function(){
                           if (curTree.get('selectedNode').get('hideChildren') == "false"){
                               curTree.collapse(curTree.get('selectedNode'))
                           } else{
                               curTree.get('selectedNode').set('hideChildren', "false", {silent: true})
                           }
            curTree.getShareCode()
            curTree.trigger('propagate')
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
