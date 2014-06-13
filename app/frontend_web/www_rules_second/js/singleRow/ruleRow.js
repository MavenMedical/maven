
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
    'models/ruleCollection',
    'text!templates/ruleRow.html'

], function ($, _, Backbone, contextModel, ruleModel, ruleCollection, ruleRowTemplate) {

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
            //update context to have a current rule, that triggers everything else
            contextModel.set({id:this.model.get("id"),
			                name:this.model.get("name")});
	        ruleModel.on('propagate:name',
			 function(model) {
			     if(contextModel.get('id') == this.model.get('id')) {
				 this.model.set({name: ruleModel.get('name')});
				 this.render()
			     } else {
		    		 ruleModel.off('propagate:name', null, this);
			     }
			 },
			 this);

        },
    	handleRemove: function() {

            var temp;
            temp = contextModel.toParams();
            temp.id = this.model.get('id');

            if (this.model.get('id')==ruleModel.get('id')) {
                                                            ruleModel.clearData();
                                                            contextModel.set({showTriggers: false, showDetails:false})
                                                           }
           this.model.url = "/rule?" + decodeURIComponent($.param(temp));
           this.model.destroy();

	       //this.model.url('/rule?' + decodeURIComponent($.param(contextModel.toParams())););
    	}
    });

    return ruleRow;

});
