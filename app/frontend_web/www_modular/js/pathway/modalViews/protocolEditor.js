
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
            CKEDITOR.replace('ProtocolText');
            CKEDITOR.replace('NoteToCopyText');


            var that = this
            this.parent = parent
                $("#detail-modal").modal({'show':'true'});
                $("#addNodeButton", this.$el).on("click", function(){
                    var protocolText = CKEDITOR.instances.ProtocolText.getData();
                    var noteToCopyText = CKEDITOR.instances.NoteToCopyText.getData();
                    that.parent.set('protocol', new Backbone.Model({protocol: protocolText, noteToCopy:noteToCopyText}))
                    $('#detail-modal').modal('hide')

            })

        }

    });
    return protocolModal
});