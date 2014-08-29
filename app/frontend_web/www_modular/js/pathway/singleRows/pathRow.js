
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
    'pathway/models/treeModel',
    'pathway/models/pathwayCollection',
    'text!templates/pathway/pathwayListEntry.html'

], function ($, _, Backbone, router, contextModel, curTree, pathwayCollection, pathRowTemplate) {

    var ruleRow = Backbone.View.extend({
        template: _.template(pathRowTemplate),
        events:{
	      'click .select-button': 'handleSelect',
	      'click .delete-button': 'handleRemove'
        },
        getRemoveUrl: function() {
            var n = contextModel.toParams()
            n.pathid = this.model.get('id')
            return '/tree?' + decodeURIComponent($.param(n));
        },
        render: function(){
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
        initialize: function(params){
            this.model = params.model
            console.log(this.model)
        },
        handleSelect: function() {
                contextModel.set('pathid', this.model.get('id'))

        },
    	handleRemove: function() {
            var n = contextModel.toParams()
            n.pathid = this.model.get('id')
            this.model.url = '/tree?' + decodeURIComponent($.param(n));
            this.model.destroy({success: function(){
                pathwayCollection.fetch()
            }})


    	}
    });

    return ruleRow;

});
