
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'pathway/models/nodeModel',
    'pathway/models/treeModel',
   'globalmodels/contextModel',
    'text!templates/pathway/NewNodeModal.html',


], function ($, _, Backbone, NodeModel,  curTree, contextModel, nodeTemplate) {

    var savingModal = Backbone.View.extend({
        template: _.template(nodeTemplate),
        el: $("#modal-target"),

        initialize: function(parent){
            var that = this

             String.prototype.htmlEscape = function() {
                 return $('<div/>').text(this.toString()).html();
            };
            this.$el.html(this.template())
            $('#addNodeButton')[0].onclick = function(){
                                   parent.unset('protocol', {silent: true})
                                   var data =  CKEDITOR.instances.newNodeSideText.getData()
                                       var n = new NodeModel({tooltip: encodeURIComponent($('#newNodeTooltip', that.$el).val()), name: encodeURIComponent($('#newNodeText', this.$el).val()), sidePanelText: encodeURIComponent(data)})
                                   that.parent.get('children').add(n)
                                   curTree.set('selectedNode', n )
                                   $('#detail-modal').modal('hide')
                          }
            var that = this
            this.parent = parent
                $("#detail-modal").modal({'show':'true'});


        }

    });
    return savingModal
});