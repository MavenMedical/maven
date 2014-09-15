/**
 * Created by Carlos Brenneisen on 9/02/14.
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
            'click .add-customer-button': 'addCustomer'
        },
        addCustomer: function () {
                var name = $("#customer-name-input").val();
                var abbr = $("#customer-abbr-input").val();
                var license = $("#customer-license-input").val();

                var reg_num = new RegExp('^[0]*[1-9]+[0]*$');
                if (!reg_num.test(license))
                {
                    $("#add-customer-message").html("Please enter a valid number for # of licenses");
                }
                else {
                    $("#add-customer-message").empty();
                    $.ajax({
                        url: "/add_customer",
                        data: $.param(contextModel.toParams()) + "&name=" + name +
                            "&abbr=" + abbr + "&license=" + license,
                        success: function () {
                            $("#add-customer-message").html("Customer Added!");
                            $("#customer-name-input").val("");
                            $("#customer-abbr-input").val("");
                            $("#customer-license-input").val("");
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