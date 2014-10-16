/**
 * Created by Carlos Brenneisen on 9/15/14.
 */

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'globalmodels/userCollection',
    'text!templates/adminSettings.html',

], function ($, _, Backbone, contextModel, userCollection, AdminSettingsTemplate) {
    var AdminModel = Backbone.Model.extend({url: '/customer_info'});

    var AdminSettings = Backbone.View.extend({
        model: null,
        target_customer: '',
        initialize: function (arg) {
            this.model = new AdminModel; //initialize every time this is shown - might not render otherwise

            var extra_data = "";
            if (typeof arg.template !== "undefined") {
                this.template = _.template(arg.template); // this must already be loaded
            }
            else {
                this.template = _.template(AdminSettingsTemplate);
            }
            if (typeof arg.target_customer !== "undefined") {
                this.target_customer = arg.target_customer;
                extra_data = "&target_customer=" + arg.target_customer;
                //this.model.attributes.target_customer = arg.target_customer;
            }
            this.model.fetch({data:$.param(contextModel.toParams()) + extra_data});
            //this.template = _.template(arg.template);
            this.model.on('change', this.render, this);
            //this.render();
        },
        events: {
            'click .setup-admin-button': 'adminSetup',
            'click .unlock-admin-button': 'unlockSettings',
            'click .lock-admin-button': 'lockSettings',
	        'change #httphttps': 'httphttps'
        },
	httphttps: function() {
	    if($("#httphttps").find(":selected").text() == 'http://') {
		alert('Http connections are inherently insecure and must not be used with operational systems.  This option is only for test, or demo systems without any ePHI only.');
	    }
	},
        unlockSettings: function() {
            $("#admin-ip-input").prop("disabled",false);
            $("#admin-name-input").prop("disabled",false);
            $("#admin-username-input").prop("disabled",false);
            $("#admin-pw-input").prop("disabled",false);
            $("#httphttps").prop("disabled",false);

            $("#admin-pw-input").val("");
            $(".lock-admin-button").show();
            $(".unlock-admin-button").hide();
        },
        lockSettings: function() {
            $("#admin-ip-input").prop("disabled",true);
            $("#admin-name-input").prop("disabled",true);
            $("#admin-username-input").prop("disabled",true);
            $("#admin-pw-input").prop("disabled",true);
            $("#httphttps").prop("disabled",true);

            $("#admin-pw-input").val("password");
            $(".lock-admin-button").hide();
            $(".unlock-admin-button").show();
        },
        adminSetup: function () {
            var ip = $("#admin-ip-input").val();
            var name = $("#admin-name-input").val();
            var pw = $("#admin-pw-input").val();
            var polling = $("#admin-polling-input").val();
            var timeout = $("#admin-timeout-input").val();
            var username = $("#admin-username-input").val();
	        var unlocked = $(".lock-admin-button").is(':visible');
	    
            var reg_num = new RegExp('^[0]*[1-9]+[0]*$');
            /*var reg_ip = new RegExp('^[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}$');
            else if (!reg_ip.test(ip))
            {
                $("#admin-setup-message").html("Please enter a valid IP Address");
            }*/
            if (!reg_num.test(polling))
            {
                $("#save-admin-message").html("Please enter a valid number for the polling interval");
            }
            else if (!reg_num.test(timeout))
            {
                $("#save-admin-message").html("Please enter a valid number for the timeout");
            }
            else if (unlocked && ip == "")
            {
                $("#save-admin-message").html("Please enter a Unity URL");
            }
            else if (unlocked && pw == "")
            {
                $("#save-admin-message").html("Please enter the password");
            }
            else {
                var protocol = $("#httphttps").find(":selected").text();
                var data;
                if (unlocked || !this.model.attributes.settings) {
                    console.log('loading from fields');
                    data = {
                        "EHRURL": $.trim(protocol) + $.trim(ip),
                        "EHRAppName": name, "EHRPassword": pw, "EHRServiceUser": username,
                        "EHRPolling": polling, "UserTimeout": timeout
                    };
                } else {
                    console.log('loading from ', this.model.attributes.settings);
                    data = _.clone(this.model.attributes.settings);
                    _.extend(data, {"EHRPolling": polling, "UserTimeout": timeout, 'locked': 'locked'});
                }

                var extra_data = "";
                if (this.target_customer != '')
                {
                    extra_data = "&target_customer=" + this.target_customer;
                }
                that = this;
                $.ajax({
                    type: 'POST',
                    dataType: 'json',
                    url: "/setup_customer?" + $.param(contextModel.toParams())+extra_data,
                    data: JSON.stringify(data),
                            success: function () {
                                $("#save-admin-message").html("Settings saved!");
                                if (unlocked || !that.model.attributes.settings) {
                                    alert("Success! Connection to EHR established.");
                                }
                                else {
                                    alert("Connection settings saved!");
                                }
                                userCollection.refresh();
                                setTimeout(userCollection.refresh, 7000);
                            },
                            error: function (resp){
                                alert("The server could NOT successfully connect using this configuration.  " + resp.responseJSON);
                                $("#save-admin-message").html("&nbsp;");
                            }
                });
            }
        },
        render: function(){
            if (this.target_customer != '') {
                this.model.attributes.settings.target_customer = this.target_customer;
            }
            this.$el.html(this.template(this.model.attributes.settings));
            return this;
        },
    });

    return AdminSettings;

});
