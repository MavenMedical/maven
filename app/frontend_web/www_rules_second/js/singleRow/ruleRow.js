/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Asmaa Aljuhani'
 * DESCRIPTION: This Javascript file handle a hierarchy of rulelist view
 *              so we can handle events easier.
 * LAST MODIFIED FOR JIRA ISSUE: MAV-97
 **************************************************************************/
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/ruleCollection',
    'models/contextModel',
    'text!templates/ruleRow.html'
], function ($, _, Backbone, ruleCollection, contextModel, ruleRowTemplate) {
    var ruleRow = Backbone.View.extend({
        tagName: 'tr',
        template: _.template(ruleRowTemplate),
        events:{
	    'click .select-button': 'handleSelect',
	    'click .remove-button': 'handleRemove'
        },
        render: function(){
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
        handleSelect: function() {
            //update context to have a current rule, 
	    //that triggers everything else
	    console.log('select this');

            contextModel.set({id: this.model.get('id')});


        },
    	handleRemove: function() {
	        ruleCollection.remove(this.model);
    	}
    });

    return ruleRow;

});
