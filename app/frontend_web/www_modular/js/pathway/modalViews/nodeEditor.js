define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'pathway/models/nodeModel',
    'pathway/models/treeModel',
    'pathway/models/treeContext',
    'globalmodels/contextModel',
    'text!templates/pathway/NewNodeModal.html',

], function ($, _, Backbone, NodeModel, curTree, treeContext, contextModel, nodeTemplate) {

    var nodeModal = Backbone.View.extend({
        template: _.template(nodeTemplate),
        el: $("#modal-target"),

        initialize: function (parent, child) {
            var that = this

            this.$el.html(this.template())
            $('#addNodeButton')[0].onclick = function () {
                parent.unset('protocol', {silent: true})
                var data = CKEDITOR.instances.newNodeSideText.getData()
                var n = new NodeModel({tooltip: $('#newNodeTooltip', that.$el).val(), name: $('#newNodeText', this.$el).val(), sidePanelText: data}, curTree)
                var location = parent.get('children').length
                if (child){
                    location = parent.get('children').indexOf(child)
                    parent.get('children').remove(child, {silent: true})
                    n.get('children').add(child, {silent: true})

                    n.set('hideChildren', 'false', {silent: true})
                    curTree.trigger('propagate')
                }
                if (that.parent.get('children').models[0]){
                    if (!that.parent.get('children').models[0].get('children')){
                       that.parent.get('children').reset()

                    }

                }

                that.parent.get('children').add(n, {at: location})

                treeModel.set('selectedNode', n, {silent: true})

                treeModel.trigger('propagate')
                $('#detail-modal').modal('hide')
            }
            var that = this
            this.parent = parent
            $("#detail-modal").modal({'show': 'true'});
            CKEDITOR.replace('newNodeSideText');

        }

    });
    return nodeModal
});
