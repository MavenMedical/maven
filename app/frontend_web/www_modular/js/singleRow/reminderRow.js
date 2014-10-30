/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Carlos Brenneisen'
 * DESCRIPTION: This Javascript file handles an individual followup
 *              so we can handle events easier.
 * LAST MODIFIED FOR JIRA ISSUE:
 **************************************************************************/
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    //Template
    'text!templates/reminderRow.html',

    'globalmodels/contextModel',

], function ($, _, Backbone, reminderRowTemplate, contextModel) {
    var ReminderRow = Backbone.View.extend({
        template: _.template(reminderRowTemplate),
        initialize: function() {
            this.render();
        },
        render: function () {
            $(".followup-header-columns").show();
            $(this.el).html(this.template($.extend({viewid: this.cid}, this.model.toJSON())));

            that = this;
            $(document).ready(function() {
                $(".reminderTime", that.$el).datepicker();
                $('#ui-datepicker-div').css('z-index', '10000 !important');

                //$(that.el).find(".deleteFollowup").click(function() {
                /*$(".sendCurrentFollowup", that.$el).click(function() {
                    that.sendFollowup("");
                });*/

                $('.followupRecipient', that.$el).autocomplete({
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
                      /*  event.preventDefault();
                        if(ui.item){
                            //fill in the autocomplete box with the display name and corresponding hidden input with the actual username
                            $(event.target).val(ui.item.label);
                            //var nameInput = "#" + event.target.id + "Name";
                            $(".followupRecipientName", that.$el).val(ui.item.value);
                        }*/

                        event.preventDefault();
                        $(event.target).parent().removeClass("has-error");
                        $(".sendCurrentFollowup", this.$el).removeAttr('disabled');
                        if(ui.item){
                            //fill in the autocomplete box with the display name and corresponding hidden input with the actual username
                            $(event.target).val(ui.item.label);
                            $(".followupRecipientName", that.$el).val(ui.item.value);
                        }
                        $(this).trigger('change');
                    },
                    change: function(event, ui) {
                        $(event.target).parent().removeClass("has-error");
                        $(".sendCurrentFollowup", this.$el).removeAttr('disabled');
                        if (!ui.item) {
                            //if the user does not select a recipient from the autocomplete
                            $(".followupRecipientName", that.$el).val("");

                            if ($(event.target).val() !== "") {
                                //cleared recipient
                                $(event.target).parent().addClass("has-error");
                                $(".sendCurrentFollowup", this.$el).prop("disabled",true)
                            }
                        }
                    },
                    autoFocus: true, //force the first value to be selected if user tabs away without selecting a recipient
                    focus: function(event, ui){
                        //prevent the auto focus from changing the value of the text box
                        event.preventDefault();
                    },
                });
            });

            return this;
        },
        events: {
	        'click .deleteFollowup': 'removeFollowup',
            'click .sendCurrentFollowup': 'sendFollowup'
        },
        removeFollowup: function(that) {
            $(this.el).remove();
            console.log("removing followup");
            //this.trigger("removeFollowup");
        },
        getCurrentParams: function() {
            var subject = $(".reminderSubject", this.el).val();
            var message = $(".reminderText", this.el).val();
            var date = $(".reminderTime", this.el).val();
            var followupRecipient = $(".followupRecipient", this.$el).val();
            var followupRecipientName = $(".followupRecipientName", this.$el).val();

            return {msg_subject: subject, msg_body: message, due: date,
                    followupRecipient: followupRecipient, followupRecipientName: followupRecipientName};
        },
        sendFollowup: function() {
            var subject = $(".reminderSubject", this.$el).val();
            var message = $(".reminderText", this.$el).val();
            var date = $(".reminderTime", this.$el).val() + "T00:00:00.000Z";
            var followupRecipientName = $(".followupRecipientName", this.$el).val();

            if (subject == ""){
                //default subject
                subject = "Followup from " + new Date().toISOString().substr(0,10);
            }

            if (followupRecipientName == ''){
                //if no recipient was designated, use the default
                followupRecipientName = $("#defaultFollowupRecipientName").val(); // "";//defaultRecipient;
            }

            var extraArg = "&userid="+contextModel.get("userid");
            if (followupRecipientName!= "")
            {
                extraArg += "&target_user=" + followupRecipientName;
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
                    alert("There was a problem sending this followup: " + subject);
                },
                success: function (){
                    $("#send-followups-message").show();
                    $("#send-followups-message").html('Followup Sent!')
                    $("#send-followups-message").fadeOut(1500);
                }
            });
        }
    });

    return ReminderRow;
});