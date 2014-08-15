/* A backbone model representing the non persistant state of the application
    defines authentication, and the currently loaded id
    any class can require the 'contextModel' and recieve the same instance of the object
*/

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
], function ($, _, Backbone) {
    
    var Context = Backbone.Model.extend({

    // the url of the context model is loging when it fetches it runs the login persistance function and gets an auth key
    //currently hard coded
	urlRoot: '/login',

        defaults: {
            stage: null,
            auth: null,
	        user: null,
	        id: null,
            showDetails: false
    },
	toParams: function() {
	    var ret = _.pick(this.attributes,['user', 'auth', 'id']);
	    for(var x in ret) {
    		if(!ret[x]) {delete ret[x];}
	    }
	    return ret;
	},
        //set the active user and get an auth key
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
