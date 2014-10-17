define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'pathway/models/treeModel',
    'text!templates/pathway/deleteModal.html'


], function ($, _, Backbone,   curTree, template) {

    var deleteDialog = Backbone.View.extend({
         template: _.template(template),
         el: '#modal-target',
         initialize: function(){
            this.$el.html(this.template())
            $('#detail-modal').modal('show')
            $('#thisNode').on('click', function(){
               curTree.deleteNode(curTree.get('selectedNode'), true)
               $('#detail-modal').modal('hide')

            })
            $('#allChildren').on('click', function(){

                curTree.deleteNode(curTree.get('selectedNode'), false)
                $('#detail-modal').modal('hide')

            })
             $('#cancel').on('click', function(){

                $('#detail-modal').modal('hide')

            })
         }



    });
    return deleteDialog
});