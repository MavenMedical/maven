define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'pathway/models/nodeModel',
    'pathway/models/treeContext',
    'globalmodels/contextModel',
     'text!templates/pathway/richTextEditor.html',


], function ($, _, Backbone, NodeModel, treeContext, contextModel, nodeTemplate) {

    var sidePanelModal = Backbone.View.extend({
        template: _.template(nodeTemplate),
        el: $("#modal-target"),

        initialize: function(){


            this.$el.html(this.template())
            $('#confirmButton')[0].onclick = function(){
                                   var data =  CKEDITOR.instances.richText.getData()
                                   treeContext.get('selectedNode').set('sidePanelText', data)
                                   $('#detail-modal').modal('hide')
                          }
            $("#detail-modal").modal({'show':'true'});
            CKEDITOR.replace('richText');

        }

    });
    return sidePanelModal
});
