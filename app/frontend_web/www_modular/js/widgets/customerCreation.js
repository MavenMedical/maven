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
                var ip = $("#customer-ip-input").val();
                var license = $("#customer-license-input").val();

                $.ajax({
                    url: "/add_customer",
                    data: $.param(contextModel.toParams()) + "&name=" + name +
                        "&ip=" + ip + "&abbr=" + abbr +
                        "&license=" + license,
                    success: function (data) {
                        console.log(data);
                    }
                });
        },
        render: function(){
            this.$el.html(this.template);
            return this;
        },
    });

    return CustomerCreation;

});