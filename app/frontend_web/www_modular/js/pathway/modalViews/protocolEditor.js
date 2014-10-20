
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'pathway/models/nodeModel',
    'pathway/models/treeModel',

    'globalmodels/contextModel',
    'text!templates/pathway/NewProtocolModal.html',



], function ($, _, Backbone, NodeModel, curTree, contextModel, nodeTemplate) {

    var protocolModal = Backbone.View.extend({
        template: _.template(nodeTemplate),
        el: $("#modal-target"),
        initialize: function(parent){
            this.$el.html(this.template())
            CKEDITOR.replace('ProtocolText');


            var that = this
            this.parent = parent
                $("#detail-modal").modal({'show':'true'});
                $("#addNodeButton", this.$el).on("click", function(){
                    var protocolText = CKEDITOR.instances.ProtocolText.getData();

                    var noteToCopyText = $('#NoteToCopyText').val()
                    var defaultRecipient = $("#defaultRecipient").val();
                    var defaultRecipientName = $("#defaultRecipientName").val();
                    var defaultQuickNote = $("#defaultQuickNote").val();
                    var myId = curTree.getNextNodeID()
                    that.parent.set('children', new Backbone.Collection([new Backbone.Model({isProtocol: true, protocol: protocolText, noteToCopy:noteToCopyText,
                                                                    defaultRecipient: defaultRecipient,
                                                                    defaultRecipientName: defaultRecipientName,
                                                                    defaultQuickNote: defaultQuickNote,
                                                                    nodeID : curTree.get('id')+':'+ myId})]))
                    $('#detail-modal').modal('hide')
                    curTree.trigger('propagate')

            })

            $('#defaultRecipient').autocomplete({
                source: function (request, response) {
                    $.ajax({
                        url: "/users",
                        term: request.term,
                        dataType: "json",
                        data: $.param(contextModel.toParams()) + "&target_user=" + request.term + "&target_role=provider",
                        success: function (data) {
                            response(data);
                        }
                    });
                },
                minLength: 3,
                select: function (event, ui) {
                    event.preventDefault();
                    if(ui.item){
                        $(event.target).val(ui.item.label);
                        $("#defaultRecipientName").val(ui.item.value);
                    }
                }
            });
        }

    });
    return protocolModal
});