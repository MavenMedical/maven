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
    'text!templates/pathway/NewProtocolModal.html'

], function ($, _, Backbone, contextModel, curTree, nodeTemplate, protocolTemplate) {

    var editNode = Backbone.View.extend({

        el: $("#modal-target"),
        initialize: function () {
            if (curTree.get('selectedNode').attributes.triggers) {
                console.log('in triggers');

            } else if (curTree.get('selectedNode').attributes.protocol) {
                this.template = _.template(protocolTemplate),
                    this.$el.html(this.template(curTree.get('selectedNode').attributes));
                $('#addNodeButton')[0].onclick = function () {
                    //var protocolText = CKEDITOR.instances.ProtocolText.getData();
                    //var noteToCopyText = CKEDITOR.instances.NoteToCopyText.getData();
                    curTree.get('selectedNode').set('protocol', $('#ProtocolText', this.$el).val());
                    curTree.get('selectedNode').set('noteToCopy', $('#NoteToCopyText', this.$el).val());
                    $('#detail-modal').modal('hide')
                }

                $("#detail-modal").modal({'show': 'true'});
                CKEDITOR.replace('ProtocolText');
                CKEDITOR.replace('NoteToCopyText');

            }else{
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