/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Carlos Brenneisen'
 * DESCRIPTION: This Javascript handles an audit row, normally shown when 
 *              hovering over a user
 **************************************************************************/
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    //Template
    'text!templates/auditRow.html',

], function ($, _, Backbone, auditRowTemplate) {

    var AuditRow = Backbone.View.extend({
        tagName: "tr class='audit-row'",
        template: _.template(auditRowTemplate),
        render: function(){
            $(this.el).html(this.template($.extend({viewid:this.cid},this.model.toJSON())));
            return this;
        }
    });

    return AuditRow;

});
