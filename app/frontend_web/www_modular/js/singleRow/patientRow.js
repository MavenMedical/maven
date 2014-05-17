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
    'globalmodels/contextModel',
    'text!templates/patientRow.html'
], function ($, _, Backbone, contextModel, patRowTemplate) {
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
            //update context to have a current patient, 
	    //that triggers everything else
            contextModel.set({key:this.model.get("key"), 
			      patients:this.model.get("id"),
			      patientName:this.model.get("name")});
        }
    });

    return patientRow;

});
