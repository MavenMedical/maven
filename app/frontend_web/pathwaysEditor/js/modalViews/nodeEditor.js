
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/nodeModel',
    'models/contextModel',
    'text!templates/NewNodeModal.html',


], function ($, _, Backbone, NodeModel,  contextModel, nodeTemplate) {

    var savingModal = Backbone.View.extend({
        template: _.template(nodeTemplate),
        el: $("#modal-target"),
        events: {
            'click #addNodeButton': 'handleConfirm'
        },
        initialize: function(parent){
            this.$el.html(this.template())
            var that = this
            this.parent = parent
                $("#detail-modal").modal({'show':'true'});


        },
        handleConfirm: function(){
               that.parent.unset('protocol', {silent: true})
               var n = new NodeModel({description: $('#newNodeDescription', this.$el).val(), name: $('#newNodeText', this.$el).val(), text: $('#newNodeText', this.$el).val()})
               that.parent.get('children').add(n)
               contextModel.set('selectedNode', n )
               $('#detail-modal').modal('hide')
        }
    });
    return savingModal
});