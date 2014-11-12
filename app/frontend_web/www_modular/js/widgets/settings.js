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
        initialize: function () {
            this.render();
        },
        events: {
            'click #save-settings': 'dosave',
            'click #update-password': 'dologin',
            'click #cancel-settings': 'docancel',
            'keyup #official-name-input':'doentersave',
            'keyup #display-name-input':'doentersave',
            'keyup #login-password':'doenterlogin',
            'keyup #login-new-password':'doenterchange'
        },
        render: function () {

	    if(contextModel.get('settingsTemplate')) {
		    var that=this;
		    require(["text!../templates/"+contextModel.get('settingsTemplate')], function(settingsTemplate) {
		        that.template = _.template(settingsTemplate);
                that.$el.html(that.template(contextModel.attributes));
		        that.newPasswordChange();
		    });
	    }
        else {
		    $("#settings-modal").modal('hide');
	    }
	    return this;
        },
	dohide: function(){
            $("#settings-modal").modal('hide');
	},
	docancel: function(){
            this.dohide();
	},
	doentersave: function(event){
	    if(event.keyCode == 13){
		this.dosave(event);
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
        var official_name = $("#official-name-input").val();
        var display_name = $("#display-name-input").val();

        $.ajax({
            url: "/save_user_settings",
            data:$.param(contextModel.toParams())+"&official_name="+official_name+"&display_name="+display_name,
            success: function(data) {
                //response(data);
                console.log("Settings saved");

            },
            error: function(xhr, textStatus, errorThrown){
                console.log("Settings failed to save");
            }
        });

        $("#settings-modal").modal('hide'); //placeholder
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
