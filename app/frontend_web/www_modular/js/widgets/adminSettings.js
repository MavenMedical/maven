/**
 * Created by Carlos Brenneisen on 9/15/14.
 */

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
], function ($, _, Backbone, contextModel) {

    var CustomerCreation = Backbone.View.extend({
        initialize: function (arg) {
            this.template = _.template(arg.template);
            this.render();
        },
        events: {
            'click .admin-setup': 'adminSetup'
        },
        adminSetup: function () {
            var ip = $("#admin-ip-input").val();
            var pw = $("#admin-pw-input").val();
            var polling = $("#admin-polling-input").val();
            var timeout = $("#admin-timeout-input").val();

            var reg_num = new RegExp('^[0]*[1-9]+[0]*$');
            if (!reg_num.test(polling))
            {
                $("#admin-setup-message").html("Please enter a valid number for the polling interval");
            }
            else {
                $("#admin-setup-message").empty();
                $.ajax({
                    url: "/admin-setup",
                    data: $.param(contextModel.toParams()) + "&ip=" + ip +
                          "&pw=" + pw + "&polling=" + polling + "&timeout="+timeout,
                    success: function () {
                        $("#admin-setup-message").html("Customer Added!");
                        $("#admin-ip-input").val("");
                        $("#admin-pw-input").val("");
                        $("#admin-polling-input").val("");
                        $("#admin-timeout-input").val("");
                    }
                });
            }
        },
        render: function(){
            this.$el.html(this.template);
            return this;
        },
    });

    return CustomerCreation;

});