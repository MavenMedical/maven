
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
    'models/contextModel',
    'models/ruleModel',
    'text!templates/sourceRow.html'

], function ($, _, Backbone, contextModel, ruleModel, sourceRowTemplate) {

    var sourceRow = Backbone.View.extend({
        template: _.template(sourceRowTemplate),
        events:{
	       'click .remove-button': 'handleRemove'
        },
        initialize: function(params){
            this.model = params.model;
            this.parent = params.parent;
            this.template = _.template(params.template)

        },
        render: function(){
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
    	handleRemove: function() {

            this.parent.remove(this.model);
    	}
    });

    return sourceRow

});
