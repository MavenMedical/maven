/**
 * Created by Asmaa Aljuhani on 9/17/14.
 */
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'pathway/models/treeContext',
    'pathway/models/treeModel',
    'text!templates/pathway/NewNodeModal.html',
    'text!templates/pathway/NewProtocolModal.html'

], function ($, _, Backbone, contextModel, treeContext, curTree, nodeTemplate, protocolTemplate) {

    var editNode = Backbone.View.extend({

        el: $("#modal-target"),
        initialize: function () {
            if (treeContext.get('selectedNode').attributes.isProtocol) {
                this.template = _.template(protocolTemplate),
                    this.$el.html(this.template(treeContext.get('selectedNode').attributes));
                $('#addNodeButton')[0].onclick = function () {
                    var protocolText = CKEDITOR.instances.ProtocolText.getData();
                    treeContext.get('selectedNode').set('protocol', protocolText);
                    treeContext.get('selectedNode').set('noteToCopy', $('#NoteToCopyText', this.$el).val());
                    $('#detail-modal').modal('hide')
                    curTree.trigger('propagate')
                }

                $("#detail-modal").modal({'show': 'true'});
                CKEDITOR.replace('ProtocolText');
                CKEDITOR.instances.ProtocolText.setData(treeContext.get('selectedNode').get('protocol'));
                $('#NoteToCopyText', this.$el).val(treeContext.get('selectedNode').get('noteToCopy'))
            }else{
                this.template = _.template(nodeTemplate),
                    this.$el.html(this.template(treeContext.get('selectedNode').attributes));
                $('#addNodeButton')[0].onclick = function () {
                    treeContext.get('selectedNode').set('name', $('#newNodeText', this.$el).val());
                    treeContext.get('selectedNode').set('tooltip', $('#newNodeTooltip', this.$el).val())
                    var data = CKEDITOR.instances.newNodeSideText.getData()
                    treeContext.get('selectedNode').set('sidePanelText', data)

                    $('#detail-modal').modal('hide')
                      curTree.trigger('propagate')
                }
                $("#detail-modal").modal({'show': 'true'});
                CKEDITOR.replace('newNodeSideText');
            }
        }

    });
    return editNode
});
