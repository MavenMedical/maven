/**
 * Created by Carlos Brenneisen on 9/02/14.
 */

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'widgets/pageOption'
], function ($, _, Backbone, contextModel,pageOption) {

    var CustomerCreation = Backbone.View.extend({
        initialize: function (arg) {
            this.template = _.template(arg.template);
            this.render();
            new pageOption({'Cutomers':['fa-user', 'customer']})
            contextModel.on('change:page', this.showhide(), this)

        },
        events: {
            'click .add-customer-button': 'addCustomer'
        },
        showhide: function(){
           // alert('page change')
            console.log('showhide',contextModel.get('page'))
            if(contextModel.get('page') == 'customer'){
                this.$el.show();
            }else{
                this.$el.hide();
            }
        },
        addCustomer: function () {
            var name = $("#customer-name-input").val();
            var abbr = $("#customer-abbr-input").val();
            var license = $("#customer-license-input").val();
            var config = $("#customer-config-input").val();
            var ituser = $("#customer-ituser-input").val();

            var reg_num = new RegExp('^[0]*[1-9]+[0]*$');
            if (!reg_num.test(license))
            {
                $("#add-customer-message").html("Please enter a valid number for # of licenses");
            }
            else if (abbr=="")
            {
                $("#add-customer-message").html("Please fill out Customer Abbreviation");
            }
            else if (name=="")
            {
                $("#add-customer-message").html("Please fill out Customer Name");
            }
            else if (ituser=="")
            {
                $("#add-customer-message").html("Please fill out IT User");
            }
            else {
                $("#add-customer-message").html("&nbsp;");
                $.ajax({
                    url: "/add_customer",
                    data: $.param(contextModel.toParams()) + "&name=" + name +
                          "&abbr=" + abbr + "&license=" + license + "&ituser=" + ituser +
                          "&config=" + config,
                    success: function (data, status, jqxhr) {
                        $("#add-customer-message").html("Customer Added!");
                        $("#customer-name-input").val("");
                        $("#customer-abbr-input").val("");
                        $("#customer-license-input").val("");
                        $("#customer-ituser-input").val("");
                        $("#add-customer-message").html("Customer added.  "+data);
                        alert(data);
                    },
                    error: function(){
                        $("#add-customer-message").html("Sorry, an error occurred");
                    }
                });
            }
        },
        render: function(){
            this.$el.html(this.template);
            return this;
        }
    });

    return CustomerCreation;

});
