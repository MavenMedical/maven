
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'pathway/models/nodeModel',
    'globalmodels/contextModel',
    'text!templates/pathway/NewProtocolModal.html',
    'singleRow/reminderRow',

], function ($, _, Backbone, NodeModel, contextModel, nodeTemplate, ReminderRow) {
    var followups;
    var protocolModal = Backbone.View.extend({
        template: _.template(nodeTemplate),
        el: $("#modal-target"),
        initialize: function(parent){
            this.$el.html(this.template())
            CKEDITOR.replace('ProtocolText');
            followups = new Array();

            var that = this
            this.parent = parent
                $("#detail-modal").modal({'show':'true'});
                $("#addNodeButton", this.$el).on("click", function(){
                    var protocolText = CKEDITOR.instances.ProtocolText.getData();

                    var noteToCopyText = $('#NoteToCopyText').val();
                    var defaultRecipient = $("#defaultRecipient").val();
                    var defaultRecipientName = $("#defaultRecipientName").val();
                    var defaultQuickNote = $("#defaultQuickNote").val();
                    var followupRecipient = $(".defaultFollowupRecipient", this.$el).val();
                    var followupRecipientName = $(".defaultFollowupRecipientName", this.$el).val();
                    var followupInfo = [];

                    $(followups).each(function() {
                        this.sendFollowup();
                        followupInfo.push(this.getCurrentParams());
                    });
                    /*

                    $(".followup").each(function(){
                        //iterate through each followup: store in protocol node and add task
                        //TODO - make this be called by the reminder row object
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
                    }*/
                    that.parent.set('protocol', new Backbone.Model({isProtocol: true, protocol: protocolText, noteToCopy:noteToCopyText,
                                                                    defaultRecipient: defaultRecipient,
                                                                    defaultRecipientName: defaultRecipientName,
                                                                    defaultQuickNote: defaultQuickNote,
                                                                    followups: followupInfo,
                                                                    defaultFollowupRecipient: followupRecipient,
                                                                    defaultFollowupRecipientName: followupRecipientName}))
                    $('#detail-modal').modal('hide')

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

            $("#add-new-followup", this.$el).on("click", function() {
                $('#followups').append("<div class='followup'></div>"); //append(followup.render().el);
                el = $('.followup', $('#followups')).last();
                var followup = new ReminderRow({model:new Backbone.Model({edit:true}), el:el});
                //followup.render();
                //followup.events();
                followups.push(followup);
                followup.$el.bind('remove', {followup:followup}, that.removeFollowup);
            });

            $('#defaultRecipient, #defaultFollowupRecipient', this.$el).autocomplete({
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
                    $(event.target).parent().removeClass("has-error");
                    $("#addNodeButton", this.$el).removeAttr('disabled');
                    if(ui.item){
                        //fill in the autocomplete box with the display name and corresponding hidden input with the actual username
                        $(event.target).val(ui.item.label);
                        var nameInput = "#" + event.target.id + "Name";
                        $(nameInput).val(ui.item.value);
                    }
                    $(this).trigger('change');
                },
                change: function(event, ui) {
                    $(event.target).parent().removeClass("has-error");
                    $("#addNodeButton", this.$el).removeAttr('disabled');
                    if (!ui.item) {
                        //if the user does not select a recipient from the autocomplete
                        var nameInput = "#" + event.target.id + "Name";
                        $(nameInput).val("");

                        if ($(event.target).val() !== "") {
                            //cleared recipient
                            $(event.target).parent().addClass("has-error");
                            $("#addNodeButton", this.$el).prop("disabled",true)
                        }
                    }
                },
                autoFocus: true, //force the first value to be selected if user tabs away without selecting a recipient
                focus: function(event, ui){
                    //prevent the auto focus from changing the value of the text box
                    event.preventDefault();
                },
            });
        },
        removeFollowup: function(event) {
            //remove reference to followup
            followups = _.without(followups, event.data.followup);
        }

    });
    return protocolModal
});