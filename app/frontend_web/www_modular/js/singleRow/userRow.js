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

], function ($, _, Backbone, userRowTemplate, contextModel, AuditList, AuditTemplate) {

    var UserRow = Backbone.View.extend({
        tagName: "tr class='user-row'",
        template: _.template(userRowTemplate),
        render: function(){
            $(this.el).html(this.template($.extend({viewid:this.cid},this.model.toJSON())));
            var that = this;
            var curTitle = null;
            var overlist = false;
            var auditElement = "#mouse-target";
            var notifications = {'desktop': 'Desktop', 'mobile': 'Mobile', 'ehrinbox': 'EHR Inbox', 'off': 'Off'};
            var currentPrimary = this.model.get("notify_primary").toLowerCase();
            var currentSecondary = this.model.get("notify_secondary").toLowerCase();

            var user = that.model.get('user_name')
            $(that.el).find(".reset-user-password").click(function(){
                $("#save-user-message").html("&nbsp;");
                $.ajax({
                    url: "/reset_password",
                    data: $.param(contextModel.toParams()) + "&target_user=" + user +
                        "&target_customer=" + that.model.get("customer_id") + "&ehr_state=" + that.model.get("ehr_state"),
                    success: function (data) {
                        if (data!=''){
                            alert(data);
                        }
                        $("#save-user-message").html("Password Reset!");
                    }
                });
            });
            
            $(that.el).find('.activate-checkbox').change(function(event) {
                console.log('clicked toggle-status', user, that.model.attributes)
                var status = "disabled";
                var button=event.target;
                if (button.checked) status = "active";
                $.ajax({
                    url: "/update_user",
                    data: $.param(contextModel.toParams()) + "&target_user=" + user +
                        "&target_customer=" + that.model.get("customer_id")+ "&state=" + status,
                    success: function (data) {
                        if (data!='TRUE'){
                            alert(data);
                        }
                        $("#save-user-message").html("User Updated!");
                        that.model.set('state', status)
                    },
                    error: function () {
                        alert("Sorry, an error occurred. Please try again later");
                        //reset switch to its prior state
                        if (status =='active'){
                            $(button).attr('checked','');
                        }
                        else {
                            $(button).attr('checked','checked');
                        }
                        var message = 
                        $("#save-user-message").html("Sorry, an error occurred. Please try again later");
                        
                    }
                });
            });
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
                    var extraData = {target_customer: that.model.get("customer_id"), target_user: user};
                    auditList = new AuditList({el: $(auditElement), template: AuditTemplate, extraData: extraData});
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


            return this;
        },
        updateNotificationPreferences: function(primary, secondary){
            var that = this
            $.ajax({
                url: "/update_user_pref",
                data: $.param(contextModel.toParams()) + "&target_user=" + this.model.get("user_name") +
                      "&target_customer=" + this.model.get("customer_id") +
                      "&notify1="+primary+"&notify2="+secondary,
                success: function () {
                    $("#save-user-message").html("User Updated!");
                    that.model.set({notify_primary: primary, notify_secondary: secondary})
                },
                error: function (){
                    alert("Could not save user information.");
                    $("#save-user-message").html("Could not save user information.");
                }
            });
        }
    })

    return UserRow;

});
