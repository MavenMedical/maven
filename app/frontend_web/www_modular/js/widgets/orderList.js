define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    //views
    'globalmodels/orderCollection',
    
    'singleRow/orderRow',
    // Using the Require.js text! plugin, we are loaded raw text
    // which will be used as our views primary template
    'text!templates/orderList.html'
], function ($, _, Backbone, orderCollection, OrderRow, orderTemplate) {

    var OrderList = Backbone.View.extend({
	template: _.template(orderTemplate),
	initialize: function() {
            var template = 
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
