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
                //show all default followups
                this.sendMode = true;
                $('#followups', that.$el).append("<div class='followup'></div>");
                el = $('.followup', $('#followups', that.$el)).last();
                var followup = new ReminderRow({model:new Backbone.Model(this), el:el});

                followups.push(followup);
                followup.$el.bind('remove', {followup:followup}, that.removeFollowup);
            })
            if (!this.attributes.followups.length) {
                //if no stored followups, initialize with one blank one
                $('#followups').append("<div class='followup'></div>");
                el = $('.followup', $('#followups')).last();
                var followup = new ReminderRow({model:new Backbone.Model({edit:true}), el:el});
                followups.push(followup);
                followup.$el.bind('remove', {followup:followup}, that.removeFollowup);
            }

            $("#add-new-followup", this.$el).on("click", function() {
                //create new followup object
                $('#followups').append("<div class='followup'></div>");
                el = $('.followup', $('#followups')).last();
                var followup = new ReminderRow({model:new Backbone.Model({edit:true, sendMode: true}), el:el});
                followups.push(followup);
                followup.$el.bind('remove', {followup:followup}, that.removeFollowup);
            });

            $("#sendFollowupsButton", this.$el).on("click", function(){
                //send all followups
                $(followups).each(function(){
                    this.sendFollowup();
                });
                alert("Followups Sent");
               $('#detail-modal').modal('hide')
            })
        },
        removeFollowup: function(event) {
            //remove reference to followup
            followups = _.without(followups, event.data.followup);
            console.log("Removing from send followups");
        }
    });
    return sendFollowups
});
