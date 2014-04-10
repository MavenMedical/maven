/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Asmaa Aljuhani'
 * DESCRIPTION: This Javascript file handle a hierarchy of orderables view
 *              so we can handle events easier.
 * LAST MODIFIED FOR JIRA ISSUE: MAV-97
 **************************************************************************/
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'currentContext',

    //Template
    'text!templates/singleRow/orderRow.html'

], function ($, _, Backbone, currentContext, orderRowTemplate) {
    var orderRow = Backbone.View.extend({
        tagName: 'div',
        template: _.template(orderRowTemplate),
        events:{
            'click .panel-heading': 'handleClick'
        },
        render: function(){
            $(this.el).append(this.template(this.model.toJSON()));
            return this;
        },
        handleClick: function(e){
             $('#'+this.model.get('id')).toggleClass("in");
        }

    });

    return orderRow;

});