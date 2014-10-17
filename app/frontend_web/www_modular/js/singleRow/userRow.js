/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Carlos Brenneisen'
 * DESCRIPTION: This Javascript file handles a hierarchy of users view
 *              so we can handle events easier.
 * LAST MODIFIED FOR JIRA ISSUE:
 **************************************************************************/
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    //Template
    'text!templates/userRow.html',

    'globalmodels/contextModel',

    'widgets/auditList',
    'text!templates/auditScroll.html',
    'libs/jquery/jquery-mousestop-event',
    'libs/bootstrap-switch/bootstrap-switch',

], function ($, _, Backbone, userRowTemplate, contextModel, AuditList, AuditTemplate) {

    var UserRow = Backbone.View.extend({
        tagName: "tr class='user-row'",
        template: _.template(userRowTemplate),
        render: function(){
            $(this.el).html(this.template($.extend({viewid:this.cid},this.model.toJSON())));
            return this;
        },
        updateNotificationPreferences: function(primary, secondary){
            $.ajax({
                url: "/update_user_pref",
                data: $.param(contextModel.toParams()) + "&target_user=" + this.model.get("user_name") +
                      "&target_customer=" + this.model.get("customer_id") +
                      "&notify1="+primary+"&notify2="+secondary,
                success: function () {
                    $("#save-user-message").html("User Updated!");
                },
                error: function (resp){
                    alert("Could not save user information.  " + resp.responseJSON);
                    $("#save-user-message").html("&nbsp;");
                }
            });
        },
        events : function() {
            var that = this;
            var curTitle = null;
            var overlist = false;
            var auditElement = "#mouse-target";
            var notifications = {'desktop': 'Desktop', 'mobile': 'Mobile', 'ehrinbox': 'EHR Inbox', 'off': 'Off'};
            var currentPrimary = this.model.get("notify_primary").toLowerCase();
            var currentSecondary = this.model.get("notify_secondary").toLowerCase();

            $(document).ready(function() {
                $(".toggle-status", that.$el).bootstrapSwitch();
                $(that.el).find(".reset-user-password").click(function(){
                    $("#save-user-message").html("&nbsp;");
                    $.ajax({
                        url: "/reset_password",
                        data: $.param(contextModel.toParams()) + "&target_user=" + that.model.get("user_name") +
                            "&target_customer=" + that.model.get("customer_id"),
                        success: function () {
                            $("#save-user-message").html("Password Reset!");
                        }
                    });
                });

                $('.toggle-status', that.$el).on('switchChange.bootstrapSwitch', function(event, state) {
                    var status = "disabled";
                    if (state) status = "active";
                    $.ajax({
                        url: "/update_user",
                        data: $.param(contextModel.toParams()) + "&target_user=" + that.model.get("user_name") +
                            "&target_customer=" + that.model.get("customer_id")+ "&state=" + status,
                        success: function (data) {
                            if (data!='TRUE'){
                                alert(data);
                            }
                            $("#save-user-message").html("User Updated!");
                        },
                        error: function () {
                            alert("Sorry, an error occurred. Please try again later");
                            $(event.target).bootstrapSwitch('toggleState', true); //reset switch to its prior state
                            $("#save-user-message").html("Sorry, an error occurred. Please try again later");
                        }
                    });
                });
/*
                $(that.el).find(".btn-status").click(function(event){
                    if ($(event.target).attr("value")=='deactivate'){
                        var state = "disabled";
                        $(event.target).attr("value", "activate");
                        $(event.target).find(".btn-hover").html("Activate");
                        $(event.target).find(".btn-label").html("Inactive");
                    }
                    else{
                        var state = "active";
                        $(event.target).attr("value", "deactivate");
                        $(event.target).find(".btn-hover").html("DeActivate");
                        $(event.target).find(".btn-label").html("Active");
                    }
                    $.ajax({
                        url: "/update_user",
                        data: $.param(contextModel.toParams()) + "&target_user=" + that.model.get("user_name") +
                            "&target_customer=" + that.model.get("customer_id")+ "&state=" + state,
                        success: function () {
                            $("#save-user-message").html("User Updated!");
                        },
                        error: function () {
                            $("#save-user-message").html("Sorry, an error occurred. Please try again later");
                        }
                    });
                });
*/
                $(".btn-msg-primary", that.$el).click(function(event){
                    currentPrimary = $(event.target).attr("value"); //update to whatever was selected
                    $(".msg-primary-label", that.$el).html(notifications[currentPrimary]); //update drop-down label
                    if (currentPrimary == 'off') {
                        //secondary notifications are disabled if primary notifications are off
                        currentSecondary = 'off';
                        $(".msg-secondary-label", that.$el).html("Off");
                        $(".msg-secondary-dropdown").prop("disabled", true);
                    }
                    else {
                        $(".msg-secondary-dropdown").prop("disabled", false);
                        if (currentPrimary == currentSecondary){
                            //secondary notifications cannot be the same as primary notifications
                            currentSecondary = 'off';
                            $(".msg-secondary-label", that.$el).html("Off");
                        }
                    }
                    that.updateNotificationPreferences(currentPrimary, currentSecondary);
                });

                $(".btn-msg-secondary", that.$el).click(function(event){
                    currentSecondary = $(event.target).attr("value"); //update to whatever was selected
                    $(".msg-secondary-label", that.$el).html(notifications[currentSecondary]); //update drop-down label
                    that.updateNotificationPreferences(currentPrimary, currentSecondary);
                });

                $(that.el).unbind('click');
                var mousepos;
                $(that.el).find(".user-state").click(function(){$("#save-user-message").empty();});

		        $(that.el).find(".audit-hover").mouseover(function() {curTitle = "audit";});
                $(that.el).find(".audit-hover").mousestop(500, function(e) {
                    if (curTitle) {
                        //mousepos=e;
                        $(auditElement).hide();
                        auditList = new AuditList({el: $(auditElement), template: AuditTemplate, targetCustomer: that.model.get("customer_id"), targetUser: that.model.get("user_name")});
                        auditList.$el[0].style.left = (mousepos.pageX + 10) + 'px';
                        auditList.$el[0].style.top = (mousepos.pageY - 50) + 'px';
                    }
                });
                $(that.el).find(".audit-hover").mouseleave(function() {
                    curTitle= null;
                    setTimeout(maybeHide,500);
                });
	            $(that.el).find(".audit-hover").mousemove(function(e) {mousepos=e;});
                $(auditElement).mouseover(function() {
                    overlist = true;
                });
                $(auditElement).mouseleave(function() {
                    overlist=false; setTimeout(maybeHide,500);
                });

                maybeHide = function() {
                    if (curTitle == null && !overlist) {
                        $(auditElement).hide();
                        overlist = false;
                    }
                }
            });
       }

    });

    return UserRow;

});
