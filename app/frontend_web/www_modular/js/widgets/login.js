/**
 * Created by Tom on 6/11/14
 */

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
], function ($, _, Backbone, contextModel) {

    var Login = Backbone.View.extend({
        initialize: function (options) {
	    contextModel.on('change:loginTemplate', this.render, this);
	    $("#login-modal").modal({'show':'true', 'backdrop':'static',keyboard:false});
	    this.render();	    
        },
	events: {
	    'click #login-button': 'dologin',
	    'click #fastlogin-button': 'fastlogin',
	    'keyup #login-user':'doenterlogin',
	    'keyup #login-password':'doenterlogin',
	},
        render: function () {
	    //currentContext.setUser('notarealpassword', Backbone.history.fragment);  // hack for now
	    if(contextModel.get('loginTemplate')) {
		var that=this;
		require(["text!../templates/"+contextModel.get('loginTemplate')], function(loginTemplate) {
		    that.template = _.template(loginTemplate);
		    that.$el.html(that.template({user:'maven', password:'maven'}));
		});
		
	    } else {
		$("#login-modal").modal('hide');
	    }
	    return this;
        },
	doenterlogin: function(event){
	    if(event.keyCode == 13){
		this.dologin();
	    }
	},
	fastlogin: function() {
	    contextModel.setUser('maven','maven', Backbone.history.fragment);
	},
	dologin: function() {
	    var user = $("#login-user").val();
	    var password = $("#login-password").val();
	    if( user && password ) {
		contextModel.setUser(user, password, Backbone.history.fragment);
	    }
	},
    });
    return Login;
});
