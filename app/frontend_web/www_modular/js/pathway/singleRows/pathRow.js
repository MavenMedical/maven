
/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Tom DuBois'
 * DESCRIPTION: This Javascript file handle a hierarchy of rulelist view
 *              so we can handle events easier.
 * 
 **************************************************************************/
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'router',
    'globalmodels/contextModel',
    'pathway/models/pathwayCollection',
    'text!templates/pathway/pathwayListEntry.html'

], function ($, _, Backbone, router, contextModel, pathwayCollection, pathRowTemplate) {

    var ruleRow = Backbone.View.extend({
        template: _.template(pathRowTemplate),
        events:{
	      'click .select-button': 'handleSelect',
	      'click .delete-button': 'handleRemove'
        },
        render: function(){
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
        initialize: function(params){
            this.model = params.model
        },
        handleSelect: function() {
                contextModel.set('pathid', String(this.model.get('pathid')))

        },
    	handleRemove: function() {
            this.model.destroy({success: function(){
                pathwayCollection.fetch()
            }})


    	}
    });

    return ruleRow;

});
