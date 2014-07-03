define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    //views
    'globalmodels/orderCollection',
    'singleRow/orderRow',
], function ($, _, Backbone, orderCollection, OrderRow) {

    var OrderList = Backbone.View.extend({
	initialize: function(arg) {
	    this.typeFilter = arg.typeFilter;
	    this.template = _.template(arg.template); // this must already be loaded
        this.$el.html(this.template({height:$(window).height()-50+'px'}));
	    orderCollection.bind('add', this.addOrder, this);
	    orderCollection.bind('reset', this.reset, this);
	    orderCollection.bind('sync', this.addAll, this);
	    //spendingModel.on('change:typeFilter', function() {
		//this.render();
	    //}, this);
	    this.render();
        var orderlist = $('.orderaccordion', this.$el);
	    orderlist.scrollTop(0);
	    orderlist.scroll(function() {
		if(orderlist.scrollTop() + orderlist.innerHeight() + 100 >= orderlist[0].scrollHeight) {
		    orderCollection.more();
		}
	    });
	},
	render: function() {
	    this.$el.html(this.template(this));
	    this.addAll();
	},
	addAll: function() {
	    this.reset();
	    var typefilter = this.typeFilter; 
	    var nonempty = false;
	    if (orderCollection.length) {
		for(order in orderCollection.models) {
		    if(!typefilter 
		       || orderCollection.models[order].get('ordertype') == typefilter) {
			this.addOrder(orderCollection.models[order]);
			nonempty = true;
		    }
		}
	    }
	    if(nonempty) {
		this.$el.show();
	    } else {
		this.$el.hide();
	    }
	},
	addOrder: function(order) {
	    var orderrow = new OrderRow({model: order});
	    $('.orderaccordion', this.$el).append(orderrow.render().el);
	    this.$el.show();
	},	
	reset: function() {
	    $('.orderaccordion', this.$el).empty();
	    this.$el.hide();
	},
    });

    return OrderList;

});
