
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
        initialize: function(){
            curTree.on('change:name', this.render,this)
        },
        render: function(){
            this.$el.html(this.template(curTree.get('selectedNode').attributes))
            return this;
        },

        events: {
            'click #editSidePanelButton': 'editSidePanel',
            'click #setNodeTitleButton' : 'editName',
            'click #setNodeDescriptionButton': 'editDescription',
            'click #deleteNodeButton': 'deleteNode'

        },
        editSidePanel: function(){
            new sidePanelEditor()
        },
        editName: function(){
            new editNode();
           /* console.log('tree', curTree.get('selectedNode').attributes.triggers);
            var newname = prompt("Enter the new title")
            if (newname)
                curTree.get('selectedNode').set('name', newname)*/
        },

        editDescription: function(){
            var newdesc = prompt("Enter the new description")
            if (newdesc)
                curTree.get('selectedNode').set('tooltip', newdesc)
        },

        editHelpText: function (){
            var newht = prompt("Enter the new description")
            if (newht)
                curTree.get('selectedNode').set('sidePanel', newht)
        },
        deleteNode: function(){
            curTree.deleteNode(curTree.get('selectedNode'))

        }

    })

    return treeNodeActionSet

});
