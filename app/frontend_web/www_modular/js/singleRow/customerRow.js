/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Carlos Brenneisen'
 * DESCRIPTION: This Javascript file is for handling customer row events
 **************************************************************************/
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'text!templates/customerRow.html'
], function ($, _, Backbone, contextModel, customerRowTemplate) {
    var customerRow = Backbone.View.extend({
        tagName: 'tr',
        template: _.template(customerRowTemplate),
        events:{
            'click': 'handleClick'
        },
        render: function(){
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
        events: function() {

        }
    });

    return customerRow;

});
