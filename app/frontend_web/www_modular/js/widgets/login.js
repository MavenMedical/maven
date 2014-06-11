/**
 * Created by Tom on 6/11/14
 */

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'text!../templates/login.html',
], function ($, _, Backbone, contextModel, loginTemplate) {

    var Login = Backbone.View.extend({
        el: '#modal-target',
        initialize: function (options) {
	    this.template=_.template(loginTemplate);
	    this.cancancel=false;
	    this.render();
        },
	events: {
	    'click #login-button': 'dologin',
	    'keyup #login-user':'doenterlogin',
	    'keyup #login-password':'doenterlogin',
	    'hide.bs.modal #login-modal': 'stopCancel',
	},
        render: function () {
	    //currentContext.setUser('notarealpassword', Backbone.history.fragment);  // hack for now
	    this.$el.html(this.template({user:'JHU1093124', password:''}));
	    $('#login-modal').modal();
	    return this;
        },
	doenterlogin: function(event){
	    if(event.keyCode == 13){
		this.dologin();
	    }
	},
	dologin: function() {
	    var user = $("#login-user").val();
	    var password = $("#login-password").val();
	    if( user && password ) {
		this.cancancel=true;
		contextModel.setUser(user, password, Backbone.history.fragment);
		$("#login-modal").modal('hide');
		$("#content").show();
		this.destroy();
	    }
	},
	stopCancel: function(e) {
	    if(!this.cancancel) {
		e.preventDefault();
		return false;
	    }
	}
    });
    return Login;
});
