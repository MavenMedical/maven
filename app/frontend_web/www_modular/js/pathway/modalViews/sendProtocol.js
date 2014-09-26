define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbones
    'pathway/models/nodeModel',
    'globalmodels/contextModel',
    'text!templates/pathway/sendProtocol.html',

], function ($, _, Backbone, NodeModel, contextModel, sendProtocolTemplate) {

    var sendProtocol = Backbone.View.extend({
        template: _.template(sendProtocolTemplate),
        el: $("#modal-target"),
        initialize: function(parent){
            this.$el.html(this.template());
            var that = this;
            this.parent = parent;

            $("#detail-modal").modal({'show':'true'});
            $("#sendProtocol", this.$el).on("click", function(){
                //var title = CKEDITOR.instances.newProtocolTitle.getData()
                //that.parent.set('protocol', new Backbone.Model({title: title}))
                $('#detail-modal').modal('hide')

            })

            $('#protocolRecipient').autocomplete({
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
                        $("#recipientUserName").val(ui.item.val);
                    }
                }
            });
        }
    });
    return sendProtocol
});