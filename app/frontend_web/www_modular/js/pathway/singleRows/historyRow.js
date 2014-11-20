/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Carlos Brenneisen'
 * DESCRIPTION: This Javascript handles the row for a historical snapshot
 *                  of a given pathway
 **************************************************************************/
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    //Template
    'text!templates/pathway/pathwayHistoryRow.html',

    'globalmodels/contextModel',

], function ($, _, Backbone, historyRowTemplate, ContextModel) {

    var AuditRow = Backbone.View.extend({
        tagName: "div class='history-row'",
        template: _.template(historyRowTemplate),
        events: {
            'click .history-checkbox': 'handleCheck'
        },
        render: function(){
            $(this.el).html(this.template($.extend({viewid:this.cid},this.model.toJSON())));
            return this;
        },
        handleCheck: function(){
            $(this.el).parent().find(".history-checkbox").switchClass("glyphicon-check", "glyphicon-unchecked")
            $(".history-checkbox", this.$el).switchClass("glyphicon-unchecked", "glyphicon-check");
        }
    });

    return AuditRow;

});
