
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/nodeModel',
    'text!templates/NewNodeModal.html',


], function ($, _, Backbone, NodeModel, nodeTemplate) {

    var savingModal = Backbone.View.extend({
        template: _.template(nodeTemplate),
        el: $("#modal-target"),
        initialize: function(parent){
            this.$el.html(this.template())
            var that = this
            this.parent = parent
                $("#detail-modal").modal({'show':'true'});
                $("#addNodeButton", this.$el).on("click", function(){
                     that.parent.unset('protocol', {silent: true})
                    that.parent.get('children').add(new NodeModel({text: $('#newNodeText', this.$el).val()}))
                    $('#detail-modal').modal('hide')

            })

        }

    });
    return savingModal
});