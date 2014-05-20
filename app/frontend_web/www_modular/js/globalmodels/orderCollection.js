define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel'
], function($, _, Backbone, contextModel) {
    OrderModel = Backbone.Model;

    var OrderCollection = Backbone.Collection.extend({
	url: '/orders',
	model: OrderModel,
	initialize: function(){
            // nothing here yet
        },
    });

    orderCollection = new OrderCollection;
    if(contextModel.get('userAuth')) {
	orderCollection.fetch({data:$.param(contextModel.toJSON())});
    }
    contextModel.on('change:patients', 
		    // this will be needed once the context filters things
		    function(cm) {
			if(true && cm.get('userAuth')) {
			    if (cm.get('patients')) {
				orderCollection.fetch({data:$.param(contextModel.toJSON())});
			    } else {
				orderCollection.reset();
			    }
			}
		    }, orderCollection);
    //alertCollection.on('all', function(en) { console.log('alertCollection: '+en);});

    return orderCollection;
});
