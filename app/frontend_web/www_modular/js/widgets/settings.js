/**
 * Created by Carlos on 7/15/14
 */

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
], function ($, _, Backbone, contextModel) {

    var Settings = Backbone.View.extend({
        initialize: function (options) {
	  //  contextModel.on('change:loginTemplate', this.render, this);
	    $("#settings-modal").modal({'show':'true', 'backdrop':'static',keyboard:false});
	    this.render();
        },
	events: {
        'click': 'dohide',
	    'click #save-button': 'dosave',
	    'click #update-password': 'dologin',
	    'click #cancel-button': 'cancel',
	    'keyup #login-user':'doenterlogin',
	    'keyup #login-password':'doenterlogin',
	    'keyup #login-new-password':'doenterchange',
	},
        render: function () {
	    //currentContext.setUser('notarealpassword', Backbone.history.fragment);  // hack for now
	    if(contextModel.get('settingsTemplate')) {
		var that=this;
		require(["text!../templates/"+contextModel.get('settingsTemplate')], function(settingsTemplate) {
		    that.template = _.template(settingsTemplate);
		    that.$el.html(that.template({user:'maven', password:'maven'}));
		    that.newPasswordChange();
		});
	    } else {
		$("#settings-modal").modal('hide');
	    }
	    return this;
        },
    dohide: function(event) {
        var target = $(event.target);
        if (!target.parents('div#settings-modal').length) {
            $("#settings-modal").modal('hide');
        }
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
	dosave: function(event) {
	    console.log(event);
	    //TODO
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
    return Settings;
});
