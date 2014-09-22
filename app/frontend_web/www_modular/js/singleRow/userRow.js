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
            return this;
        },
        events : function() {
            var that = this;
            var curTitle = null;
            var overlist = false;
            var auditElement = "#mouse-target";

            $(document).ready(function() {

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

                $(that.el).find(".user-state").click(function(event) {
                    var state = "disabled";
                    if ($(event.target).is(':checked')) {
                        state = "active";
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

                $(that.el).unbind('click');
                var mousepos;
                $(that.el).find(".user-state").click(function(){$("#save-user-message").empty();});

		        $(that.el).find(".audit-hover").mouseover(function() {curTitle = "audit";});
                $(that.el).find(".audit-hover").mousestop(500, function(e) {
                    if (curTitle) {
                        //mousepos=e;
                        $(auditElement).hide();
                        auditList = new AuditList({el: $(auditElement), template: AuditTemplate, targetCustomer: that.model.get("customer_id"), targetProvider: that.model.get("prov_id")});
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
