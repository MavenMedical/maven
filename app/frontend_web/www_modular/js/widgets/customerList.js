define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    //views
    'globalmodels/customerCollection',
    'singleRow/customerRow',

    'globalmodels/contextModel'
], function ($, _, Backbone, customerCollection, CustomerRow, contextModel) {

    var CustomerList = Backbone.View.extend({
	initialize: function(arg) {
	    this.typeFilter = arg.typeFilter;
	    this.template = _.template(arg.template); // this must already be loaded
        this.$el.html(this.template({height:$(window).height()-50+'px'}));
	    customerCollection.bind('add', this.addCustomer, this);
	    customerCollection.bind('reset', this.reset, this);
	    customerCollection.bind('sync', this.addAll, this);
	    //spendingModel.on('change:typeFilter', function() {
		//this.render();
	    //}, this);
	    this.render();
        var customerlist = $('.customeraccordion', this.$el);
	    customerlist.scrollTop(0);
	    customerlist.scroll(function() {
		if(customerlist.scrollTop() + customerlist.innerHeight() + 100 >= customerlist[0].scrollHeight) {
		    customerCollection.more();
		}
	    });
	},
    events: {
	    'click #save-customer-changes': 'saveChanges',
    },
    saveChanges: function() {
      /*  that = this;
        $(".customer-row").each(function () {
            var customer_id  = $(this).find(".customer-val-id").html();
            var state="disabled";
            if($(this).find('.customer-state').is(':checked'))
            {
                    state = "active";
            }
            $.ajax({
                url: "/update_customer",
                data: $.param(contextModel.toParams()) + "&target_customer=" + customer_id +
                                                         "&state=" + state,
                success: function (data) {
                    console.log(data);
                }
            });
        });*/
    },
	render: function() {
	    this.$el.html(this.template(this));
	    this.addAll();
	},
	addAll: function() {
	    this.reset();
	    var typefilter = this.typeFilter; 
	    var nonempty = false;
	    if (customerCollection.length) {
		for(customer in customerCollection.models) {
			this.addCustomer(customerCollection.models[customer]);
			nonempty = true;
		}
	    }
	    if(nonempty) {
		this.$el.show();
	    } else {
		this.$el.hide();
	    }

        var customerlist = $('.customeraccordion', this.$el);
        setTimeout(function() {
            var customerHeight = customerlist.innerHeight();
            if (customerHeight > 0 && customerHeight < parseInt(customerlist.css('max-height'))) {
                customerCollection.more();
            }
        },500);
	},
	addCustomer: function(customer) {
	    var customerrow = new CustomerRow({model: customer});
	    $('.customertable').append(customerrow.render().el);
	    this.$el.show();
        customerrow.events();
	},	
	reset: function() {
	    $('.customertable > tbody', this.$el).empty();
	    this.$el.hide();
	},
    });

    return CustomerList;

});
