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
	    'click #update-password': 'dologin',
	    'click #fastlogin-button': 'fastlogin',
	    'keyup #login-user':'doenterlogin',
	    'keyup #login-password':'doenterlogin',
	    'keyup #login-new-password':'doenterchange',
	},
        render: function () {
	    //currentContext.setUser('notarealpassword', Backbone.history.fragment);  // hack for now
	    if(contextModel.get('loginTemplate')) {
		var that=this;
		require(["text!../templates/"+contextModel.get('loginTemplate')], function(loginTemplate) {
		    that.template = _.template(loginTemplate);
		    that.$el.html(that.template({user:'maven', password:'maven'}));
		    that.newPasswordChange();
		});
	    } else {
		$("#login-modal").modal('hide');
	    }
	    return this;
        },
	doenterlogin: function(event){
	    if(event.keyCode == 13){
		this.dologin(event);
	    }
	},
	doenterchange: function(event){
	    if(event.keyCode == 13){
		this.dologin(event);
	    } else {
		this.newPasswordChange();
	    }
	},
	fastlogin: function() {
	    contextModel.setUser('maven','mavendevel', Backbone.history.fragment);
	},
	dologin: function(event) {
	    console.log(event);
	    var user = $("#login-user").val();
	    var password = $("#login-password").val();
	    if( user && password ) {
		var jqnewpassword = $("#login-new-password");
		if(!jqnewpassword.is(":visible")) {
		    contextModel.setUser(user, password, null);
		} else {
		    if(this.newPasswordChange()) {
			contextModel.setUser(user, password, jqnewpassword.val());
		    } else {

		    } 
		} 
	    }
	},
	newPasswordChange: function() {
	    var newpw = $("#login-new-password").val();
	    var check = "<big><big><font color='#00b000'>&#x2714</font></big></big>";
	    var X = "<big><font color='#ff0000'>&#x2718</font></big>";
	    var len = newpw.length<8;
	    var low = newpw.search(".*[a-z]")<0;
	    var up = newpw.search(".*[A-Z]")<0;
	    var num = newpw.search(".*[0-9]")<0;
	    var diff = newpw==$("#login-password").val();
	    $("#pw-len-cb").html(len?X:check);
	    $("#pw-low-cb").html(low?X:check);
	    $("#pw-up-cb").html(up?X:check);
	    $("#pw-num-cb").html(num?X:check);
	    $("#pw-diff-cb").html(diff?X:check);
	    if(len || low || up || num || diff) {
		$("#login-button").attr("disabled", "disabled");
		return false;
	    } else {
		$("#login-button").removeAttr("disabled");
		return true;
	    }
	}
    });
    return Login;
});
