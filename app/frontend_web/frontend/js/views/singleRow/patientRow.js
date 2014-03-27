/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Asmaa Aljuhani'
 * DESCRIPTION: This Javascript file handle a hierarchy of patientlist view
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
    'text!templates/singleRow/patientRow.html'

], function ($, _, Backbone, currentContext, patRowTemplate) {
    var patientRow = Backbone.View.extend({
        tagName: 'tr',
        template: _.template(patRowTemplate),
        events:{
            'click': 'handleClick'
        },
        render: function(){
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
        handleClick: function(){
            console.log(this.model.get("name"));
            //update context
            currentContext.key = this.model.get("key");
            currentContext.patients = this.model.get("id");


        }

    });

    return patientRow;

});