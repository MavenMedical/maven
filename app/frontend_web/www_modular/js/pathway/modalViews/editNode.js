/**
 * Created by Asmaa Aljuhani on 9/17/14.
 */
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'pathway/models/treeModel',
    'text!templates/pathway/NewNodeModal.html',

], function ($, _, Backbone, contextModel, curTree, nodeTemplate) {

    var editNode = Backbone.View.extend({

        el: $("#modal-target"),
        initialize: function () {
            if (curTree.get('selectedNode').attributes.triggers) {
                console.log('in triggers');

            } else {
                this.template = _.template(nodeTemplate),
                    this.$el.html(this.template(curTree.get('selectedNode').attributes));
                $('#addNodeButton')[0].onclick = function () {
                    curTree.get('selectedNode').set('name', $('#newNodeText', this.$el).val());
                    curTree.get('selectedNode').set('tooltip', $('#newNodeTooltip', this.$el).val())
                    var data = CKEDITOR.instances.newNodeSideText.getData()
                    curTree.get('selectedNode').set('sidePanelText', data)

                    $('#detail-modal').modal('hide')
                }
                $("#detail-modal").modal({'show': 'true'});
                CKEDITOR.replace('newNodeSideText');
            }
        }

    });
    return editNode
});