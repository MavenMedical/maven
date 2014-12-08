/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Carlos Brenneisen'
 * DESCRIPTION: This Javascript handles an interaction row, normally shown when 
 *              hovering over a user
 **************************************************************************/
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    //Template
    'text!templates/interactionRow.html',

], function ($, _, Backbone, interactionRowTemplate) {

    var InteractionRow = Backbone.View.extend({
        tagName: "tr class='interaction-row'",
        template: _.template(interactionRowTemplate),
        render: function(){
            $(this.el).html(this.template($.extend({viewid:this.cid},this.model.toJSON())));
            return this;
        }
    });

    return InteractionRow;

});
