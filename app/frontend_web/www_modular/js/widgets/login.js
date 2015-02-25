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
	    contextModel.on('change:loginTemplate change:login-message', this.render, this);
	    $("#login-modal").modal({'show':'true', 'backdrop':'static',keyboard:false});
	    this.user = '';
	    this.customer = '';
	    this.render();
	    var that = this
	    var domains = location.hostname.split('.')
	    if (domains.length == 3) {
		$.ajax({type: 'GET',dataType: 'json',url: "/customer_id?abbr=" + domains[0],
		       success: function(data) {
			   that.fixed_customer = data
			   var cust = $("#login-customer")
			   cust.val(data)
			   cust.hide()
		       }})
	    }
        },
	events: {
	    'click #login-button': 'dologin',
	    'click #update-password': 'dologin',
	    'keyup #login-user':'doenterlogin',
	    'keyup #login-password':'doenterlogin',
	    'keyup #login-new-password':'doenterchange',
	    'click #reset-password': 'resetpassword',
	},
	resetpassword: function() {
	    var that=this
	    var text = 'text!/services/recaptcha'
	    require(['text!../templates/resetPassword.html', text, '//www.google.com/recaptcha/api/js/recaptcha_ajax.js'], 
		    function(resetTemplate, recaptcha_key) {
			var compiled = _.template(resetTemplate)
			that.$el.html(compiled())
			Recaptcha.create(recaptcha_key, 'recaptcha-div', {callback: Recaptcha.focus_response_field})
			$('#send-reset-password').click(function() {
			    var user = $('#ehr-user').val()
			    var customer = $('#reset-customer').val()
			    var response = $('#recaptcha_response_field').val()
			    var challenge = $('#recaptcha_challenge_field').val()
			    $.ajax({
				url: '/send_reset_password',
				data: {
				    'user': user,
				    'customer_id': customer,
				    'recaptcha_challenge_field': challenge,
				    'recaptcha_response_field': response
				},
				success: function() {alert('A reset password message has been sent to this account.')},
				error: function() {
				    alert('We could not verify your recaptcha response.  Try again, or contact IT about directly resetting your password.')
				    Recaptcha.reload()
				}
			    })
			})
		    })
	},
        render: function () {
	    if(contextModel.get('loginTemplate')) {
		var that=this;
		require(["text!../templates/"+contextModel.get('loginTemplate')], function(loginTemplate) {
		    that.template = _.template(loginTemplate);
		    that.$el.html(that.template(contextModel.attributes));
		    if (that.fixed_customer) {
			var cust = $("#login-customer")
			cust.val(that.fixed_customer)
			cust.hide()
		    }
		    var message = contextModel.get('login-message');
		    if (message)
			setTimeout(function() {$('#login-message').text(message);}, 500);
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
	dologin: function(event) {
	    var user = $("#login-user").val();
	    var customer = $("#login-customer").val();
	    this.user = user;
	    this.customer = customer;
	    var password = $("#login-password").val();
	    var oauth = $("#login-oauth").val();
	    if( user && (password || oauth)) {
		var jqnewpassword = $("#login-new-password");
		$('#login-message').text('Trying to log in');
		if(!jqnewpassword.is(":visible")) {
		    contextModel.setUser(user, password, oauth, customer, null);
		} else {
		    if(this.newPasswordChange()) {
			contextModel.setUser(user, password, oauth, customer, jqnewpassword.val());
		    } else {

		    } 
		} 
	    }
	},
	newPasswordChange: function() {
	    var newpw = $("#login-new-password").val();
	    if (!newpw) return false;
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
		return false;
	    } else {
		return true;
	    }
	}
    });
    return Login;
});
