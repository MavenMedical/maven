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
    'text!templates/reminderRow.html',

    'globalmodels/contextModel',

], function ($, _, Backbone, reminderRowTemplate, contextModel) {
    var ReminderRow = Backbone.View.extend({
        template: _.template(reminderRowTemplate),
        render: function () {
            $(this.el).html(this.template($.extend({viewid: this.cid}, this.model.toJSON())));
            return this;
        },
        events : function() {
            that = this;
                            $(".reminderTime").datepicker();
            $(document).ready(function() {
                $('#ui-datepicker-div').css('z-index', '10000 !important');
            });

        }
    });

    return ReminderRow;
});