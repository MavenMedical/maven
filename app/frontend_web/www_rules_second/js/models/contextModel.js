/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 
 * DESCRIPTION: This Javascript file is for context that will be used within
 *              the application.
 *              This file needed to be called in all other modules.
 * PREREQUISITE: libraries should be predefine in main.js
 * LAST MODIFIED FOR JIRA ISSUE: MAV-98
 **************************************************************************/

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
], function ($, _, Backbone) {
    
    var Context = Backbone.Model.extend({
	urlRoot: '/login',

        defaults: {
            stage: null,
            auth: null,
	        user: null,
	        id: null,
            showTriggerEditor: false,
            showDetails: false


        },
	toParams: function() {
	    var ret = _.pick(this.attributes,['user', 'auth', 'id']);
	    for(var x in ret) {
    		if(!ret[x]) {delete ret[x];}
	    }
	    return ret;
	},
        setUser: function (user, pw, route) {
	    if (this.user != user || !this.userAuth) {
		this.set('user', user);
		//alert('setting user');
		this.fetch({
		    data: JSON.stringify({user:user, password:pw}),
		    type: 'POST',
		    success: function() {
			    Backbone.history.loadUrl(route);
		    }
		});
	    }
	}
    });

    return new Context;
});
