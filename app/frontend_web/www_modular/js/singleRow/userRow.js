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
        tagName: 'tr',
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

		        $(that.el).mouseover(function() {curTitle = "audit";});
                $(that.el).mousestop(500, function(e) {
                    if (curTitle) {
                        //mousepos=e;
                        auditList = new AuditList({el: $(auditElement), template: AuditTemplate, targetUser: that.model.get("user_id")});
                        auditList.$el[0].style.left = (mousepos.pageX + 10) + 'px';
                        auditList.$el[0].style.top = (mousepos.pageY - 50) + 'px';
                        //console.log(that.model.get("user_id"));

                    }
                });
                $(that.el).mouseleave(function() {
                    curTitle= null;
                    setTimeout(maybeHide,500);
                });
	            $(that.el).mousemove(function(e) {mousepos=e;});
                $(auditElement).mouseover(function() {
                    overlist = true;
                });
                $(auditElement).mouseleave(function() {
                    overlist=false; setTimeout(maybeHide,500);
                });

                maybeHide = function() {
                    if (curTitle == null && !overlist) {
                        //auditList.title = null;
                        auditList.$el.hide();
                       // orderList.typeFilter = 'does not exist';
                        overlist = false;
                    }
                }

/*
                $(that.el).on('click', function (e) {

                    //only grab audit data if request has not already been made
                    if ($(that.el).find(".useraudits").is(':empty')) {
                        $.ajax({
                            url: "/audits",
                            data: $.param(contextModel.toParams()) + "&target_user=" + that.model.get("user_id"),
                            success: function (data) {
                                for (var i = 0; i < data.length; i++) {
                                    $(that.el).find(".useraudits").append(data[i].date + " - " + data[i].action);
                                   /* var auditrow = new AlertRow({model: data[i]});
                                    alertrow.render = function () {
                                        $(this.el).html(this.template(this.model));
                                        return this;
                                    };
                                    //$(that.el).html(this.template(this.model.toJSON()));
                                    $(that.el).find(".orderalerts").append(alertrow.render().el);

                                    // $(that.el).find(".orderalerts").append(data[i].alerttype + ": " + data[i].html);
                                }
                            }
                        });
                    }
                });*/
            });
       }

    });

    return UserRow;

});