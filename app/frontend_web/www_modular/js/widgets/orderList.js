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
	    this.template = _.template(arg.template); // this must already be loaded
	    this.$el.html(this.template());
	    orderCollection.bind('add', this.addOrder, this);
	    orderCollection.bind('reset', this.reset, this);
	    //orderCollection.bind('remove', this.remove, this);
	    orderCollection.bind('sync', this.addAll, this);
	    this.addAll();
	},
	addOrder: function(order) {
	    var orderrow = new OrderRow({model: order});
	    $('#orderaccordion').append(orderrow.render().el);
	    this.$el.show();
	},	
	addAll: function() {
	    this.reset();
	    if (orderCollection.length) {
		for(order in orderCollection.models) {
		    this.addOrder(orderCollection.models[order]);
		}
		this.$el.show();
	    } else {
		this.$el.hide();
	    }
	},
	reset: function() {
	    $('#orderaccordion').empty();
	    this.$el.hide();
	}
    });

    return OrderList;

});
