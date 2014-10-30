define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbones
    'pathway/models/nodeModel',
    'globalmodels/contextModel',
    'text!templates/pathway/sendFollowups.html',
    'singleRow/reminderRow',

], function ($, _, Backbone, NodeModel, contextModel, sendFollowupsTemplate, ReminderRow) {

    var followups;

    var sendFollowups = Backbone.View.extend({
        template: _.template(sendFollowupsTemplate),
        el: $("#modal-target"),
        initialize: function(parent){
            var that = this;
            this.parent = parent;
            this.$el.html(this.template(this.attributes));
            $("#detail-modal").modal({'show':'true'});

            followups = new Array();
            $(this.attributes.followups).each(function(){
                this.sendMode = true;
                //var followup = new ReminderRow({model:new Backbone.Model(this)});
                $('#followups', that.$el).append("<div class='followup'></div>"); //append(followup.render().el);
                el = $('.followup', $('#followups', that.$el)).last();
                var followup = new ReminderRow({model:new Backbone.Model(this), el:el});
                //$('#followups', that.$el).append(followup.render().el);
                //followup.events();
                followups.push(followup);
                followup.$el.bind('remove', {followup:followup}, that.removeFollowup);
            })

            $("#add-new-followup", this.$el).on("click", function() {
                $('#followups').append("<div class='followup'></div>"); //append(followup.render().el);
                el = $('.followup', $('#followups')).last();
                var followup = new ReminderRow({model:new Backbone.Model({edit:true, sendMode: true}), el:el});
                //followup.render();
                //followup.events();
                followups.push(followup);
                followup.$el.bind('remove', {followup:followup}, that.removeFollowup);
            });

            $("#sendFollowupsButton", this.$el).on("click", function(){
                $(followups).each(function(){
                    this.sendFollowup();
/*
                    //iterate through each followup: store in protocol node and add task
                    var subject = $(this).find(".reminderSubject").val();
                    var message = $(this).find(".reminderText").val();
                    var date = $(this).find(".reminderTime").val() + "T00:00:00.000Z";

                    if (subject == ""){
                        //default subject
                        subject = "Followup from " + new Date().toISOString().substr(0,10);
                    }
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
                        });*/
                });
            })
        },
        removeFollowup: function(event) {
            //remove reference to followup
            //followups.splice(event.data.followup,1);
            followups = _.without(followups, event.data.followup);
            console.log("Removing from send followups");
        }
    });
    return sendFollowups
});
