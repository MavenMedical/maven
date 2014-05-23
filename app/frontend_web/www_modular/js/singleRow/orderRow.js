/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Asmaa Aljuhani'
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
    'text!templates/orderRow.html'

], function ($, _, Backbone, orderRowTemplate) {

    var OrderRow = Backbone.View.extend({
        tagName: 'div',
        template: _.template(orderRowTemplate),
        render: function(){
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },

    });

    return OrderRow;

});
