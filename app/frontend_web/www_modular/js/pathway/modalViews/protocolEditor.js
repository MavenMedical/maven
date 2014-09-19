
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'pathway/models/nodeModel',
    'text!templates/pathway/NewProtocolModal.html',


], function ($, _, Backbone, NodeModel, nodeTemplate) {

    var protocolModal = Backbone.View.extend({
        template: _.template(nodeTemplate),
        el: $("#modal-target"),
        initialize: function(parent){
            this.$el.html(this.template())
            CKEDITOR.replace('newProtocolTitle');

            var that = this
            this.parent = parent
                $("#detail-modal").modal({'show':'true'});
                $("#addNodeButton", this.$el).on("click", function(){
                    var title = CKEDITOR.instances.newProtocolTitle.getData()
                    that.parent.set('protocol', new Backbone.Model({title: title}))
                    $('#detail-modal').modal('hide')

            })

        }

    });
    return protocolModal
});