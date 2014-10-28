
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'pathway/models/nodeModel',
    'pathway/models/treeModel',
    'globalmodels/contextModel',
    'text!templates/pathway/NewProtocolModal.html',
    'singleRow/reminderRow',

], function ($, _, Backbone, NodeModel, curTree, contextModel, nodeTemplate, ReminderRow) {

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

                    var noteToCopyText = $('#NoteToCopyText').val();
                    var defaultRecipient = $("#defaultRecipient").val();
                    var defaultRecipientName = $("#defaultRecipientName").val();
                    var defaultQuickNote = $("#defaultQuickNote").val();
                    var followups = [];
                    var followupRecipient = $("#followupRecipient").val();
                    var followupRecipientName = $("#followupRecipientName").val();

                    $(".followup").each(function(){
                        //iterate through each followup: store in protocol node and add task
                        var subject = $(this).find(".reminderSubject").val();
                        var message = $(this).find(".reminderText").val();
                        var date = $(this).find(".reminderTime").val() + "T00:00:00.000Z";

                        if (subject == ""){
                            //default subject
                            subject = "Followup from " + new Date().toISOString().substr(0,10);
                        }
                        followups.push({msg_subject: subject, msg_body: message, due: date});
                        var extraArg = "&userid="+contextModel.get("userid");
                        if (followupRecipient!="" && followupRecipientName!= "")
                        {
                            extraArg += "&target_user=" + $("#followupRecipientName").val();
                        }
                        $.ajax({
                            type: 'POST',
                            dataType: 'json',
                            url: "/add_task?" + $.param(contextModel.toParams()) + extraArg,
                            data: JSON.stringify({
                                "msg_subject": subject,
                                "msg_body": message,
                                "delivery": "ehrinbox",
                                "due": date,
                            }),
                            error: function (){
                                alert("There was a problem setting up followups.");
                            }
                        });

                    });
                    if (followups.length <= 0) {
                        followupRecipient = "";
                        followupRecipientName = "";
                    }
                    var myId = curTree.getNextNodeID()
                    that.parent.set('children', new Backbone.Collection([
                                                                new Backbone.Model({isProtocol: true, protocol: protocolText, noteToCopy:noteToCopyText,
                                                                    defaultRecipient: defaultRecipient,
                                                                    defaultRecipientName: defaultRecipientName,
                                                                    defaultQuickNote: defaultQuickNote,
                                                                    followups: followups,
                                                                    followupRecipient: followupRecipient,
                                                                    followupRecipientName: followupRecipientName,
                                                                    nodeID : curTree.get('id')+':'+ myId})]))
                    $('#detail-modal').modal('hide')
                    curTree.trigger('propagate')

            })

            $("#show-advanced-settings", this.$el).on("click", function(event){
                if($(".advanced-settings", that.$el).is(":visible")){
                    $(event.target).attr("class", "glyphicon glyphicon-chevron-right");
                    $(".advanced-settings", that.$el).slideUp();
                }
                else {
                    $(event.target).attr("class", "glyphicon glyphicon-chevron-down");
                    $(".advanced-settings", that.$el).slideDown();
                }
            });

            $("#add-new-followup", this.$el).on("click", function(event) {
                var followup = new ReminderRow({model:new Backbone.Model});
                $('#followups').append(followup.render().el);
                followup.events();
            });

            $('#defaultRecipient, #followupRecipient').autocomplete({
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
                        //fill in the autocomplete box with the display name and corresponding hidden input with the actual username
                        $(event.target).val(ui.item.label);
                        var nameInput = "#" + event.target.id + "Name";
                        $(nameInput).val(ui.item.value);
                    }
                }
            });
        }

    });
    return protocolModal
});