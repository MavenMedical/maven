/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Asmaa Aljuhani'
 * DESCRIPTION: This Javascript file handle a hierarchy of alerts view
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
    'text!templates/singleRow/alertRow.html'

], function ($, _, Backbone, currentContext, alertRowTemplate) {
    var alertRow = Backbone.View.extend({
        tagName: 'div',
        template: _.template(alertRowTemplate),
        events:{
            'click': 'handleClick'
        },
        render: function(){
            console.log(this.model.toJSON());
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
        handleClick: function(){

            $('#collapse'+this.model.get('patient')+'-'+this.model.get('id')).toggleClass("in");
                    }

    });

    return alertRow;

});