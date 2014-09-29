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
            userAuth: null,
	        user: "cliffhux",
            customer_id: "2",
	        id: null,
            showDetails: false
    },
	toParams: function() {
	    //console.log(this);
        console.log("contextModel", this.userAuth)
	    var ret = _.pick(this.attributes,['user','provider','startdate','enddate','encounter',
		 			      'patients','department','userAuth', 'customer_id',
					      'roles', 'pathid', 'userid']);
        ret.id = ret.pathid
	    //console.log(ret);
	    for(var x in ret) {
		if(ret[x] === null || (x != 'provider' && ret[x] === '')) {delete ret[x];}
	    }
	    return ret;
	},
        //set the active user and get an auth key
    setUser: function (user, pw, route) {
	    if (this.user != user || !this.userAuth) {
        var that = this
		alert('setting user');
		this.fetch({

		    data: JSON.stringify({user:"CLIFFHUX", customer_id: "2", password:"maven"}),

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
