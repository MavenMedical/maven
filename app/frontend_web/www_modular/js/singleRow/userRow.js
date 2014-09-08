/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Carlos Brenneisen'
 * DESCRIPTION: This Javascript file handle a hierarchy of orders view
 *              so we can handle events easier.
 * LAST MODIFIED FOR JIRA ISSUE: MAV-97
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
          //Load alerts related to this order whenever the detail portion is expanded

            var that = this;
            var curTitle = null;
            var overlist = false;
            var auditElement = "#mouse-target";

            $(document).ready(function() {
                $(that.el).unbind('click');
                var mousepos;
                //$(that.el).mousemove(function(e) {mousepos=e;});
                $(that.el).find(".user-state").click(function(){$("#save-user-message").empty();});

		        $(that.el).find(".audit-hover").mouseover(function() {curTitle = "audit";});
                $(that.el).find(".audit-hover").mousestop(500, function(e) {
                    if (curTitle) {
                        //mousepos=e;
                        $(auditElement).hide();
                        auditList = new AuditList({el: $(auditElement), template: AuditTemplate, targetCustomer: that.model.get("customer_id"), targetProvider: that.model.get("prov_id")});
                        auditList.$el[0].style.left = (mousepos.pageX + 10) + 'px';
                        auditList.$el[0].style.top = (mousepos.pageY - 50) + 'px';
                        //console.log(that.model.get("user_id"));

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
                        //auditList.title = null;
                        $(auditElement).hide();
                       // orderList.typeFilter = 'does not exist';
                        overlist = false;
                    }
                }


            });
       }

    });

    return UserRow;

});
