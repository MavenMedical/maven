/**
 * Created by Carlos Brenneisen on 9/15/14.
 */

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
], function ($, _, Backbone, contextModel) {
    var AdminModel = Backbone.Model.extend({url: '/customer_info'});
    var adminModel = new AdminModel;

    var AdminSettings = Backbone.View.extend({
        model: adminModel,
        initialize: function (arg) {
            this.model.fetch({data:$.param(contextModel.toParams())});
            this.template = _.template(arg.template);
            this.model.on('change', this.render, this);
            //this.render();
        },
        events: {
            'click .setup-admin-button': 'adminSetup'
        },
        adminSetup: function () {
            var ip = $("#admin-ip-input").val();
            var name = $("#admin-name-input").val();
            var pw = $("#admin-pw-input").val();
            var polling = $("#admin-polling-input").val();
            var timeout = $("#admin-timeout-input").val();

            var reg_num = new RegExp('^[0]*[1-9]+[0]*$');
            if (!reg_num.test(polling))
            {
                $("#admin-setup-message").html("Please enter a valid number for the polling interval");
            }
            else if (!reg_num.test(timeout))
            {
                $("#admin-setup-message").html("Please enter a valid number for the timeout");
            }
            else {
                $("#admin-setup-message").empty();
                $.ajax({
                    url: "/setup_customer",
                    data: $.param(contextModel.toParams()) + "&ip=" + ip + "&name=" + name +
                          "&password=" + pw + "&polling=" + polling + "&timeout="+timeout,
                    success: function () {
                        $("#save-admin-message").html("Settings saved!");
                    }
                });
            }
        },
        render: function(){
            this.$el.html(this.template(this.model.attributes.settings));
            return this;
        },
    });

    return AdminSettings;

});