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
            $(document).ready(function(){
                $("#sendProtocolNote", that.$el).val(that.attributes.protocol.defaultQuickNote);
                $("#protocolRecipient", that.$el).val(that.attributes.protocol.defaultRecipient);
                $("#recipientUserName", that.$el).val(that.attributes.protocol.defaultRecipientName);
            });

            $("#sendProtocolButton", this.$el).on("click", function(){
                //var title = CKEDITOR.instances.newProtocolTitle.getData()
                //that.parent.set('protocol', new Backbone.Model({title: title}))
                $('#detail-modal').modal('hide')
                var message = $("#sendProtocolNote").val() + "\r\n " + contextModel.get("official_name") +
                                " would like you to review this patient. \r\n" +
                                window.location.protocol + "//" + window.location.host + "#pathways/" + contextModel.get("pathid") +
                                    "/patient/" + contextModel.get("patients") + "/" + new Date().toISOString().substr(0,10) + "\r\n" +
                                that.attributes.protocol.protocol.replace("<p>", "").replace("</p>","\r\n").replace("&nbsp;", " ").replace("<br />","\r\n");
                $.ajax({
                    type: 'POST',
                    dataType: 'json',
                    url: "/send_message?" + $.param(contextModel.toParams()) + "&target_user="+$("#recipientUserName").val(),
                    data: JSON.stringify({
                        "subject": "Please review this patient - " + contextModel.get("official_name"),
                        "message": message,
                    }),
                    success: function () {
                        $("#save-admin-message").html("Settings saved!");
                            alert("Success! Connection to EHR established.");
                            userCollection.refresh();
                            setTimeout(userCollection.refresh, 7);
                    },
                    error: function (){
                        alert("The server could NOT successfully connect using this configuration.");
                        $("#save-admin-message").html("&nbsp;");
                    }
                });
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
                        $("#recipientUserName").val(ui.item.value);
                    }
                }
            });
        }
    });
    return sendProtocol
});