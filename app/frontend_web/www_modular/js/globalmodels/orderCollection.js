define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel'
], function($, _, Backbone, contextModel) {
    OrderModel = Backbone.Model;

    var OrderCollection = Backbone.Collection.extend({
	//url: '/orders',
    url: function() {return '/orders/'+this.offset+'-'+(this.offset+this.limit);},
    limit: 3,
    tried: 0,
    offset: 0,
	model: OrderModel,
	initialize: function(){
            // nothing here yet
        },
    more: function() {
	    if(this.tried <= this.models.length) {
            this.offset = this.models.length;
            this.tried = this.models.length+this.limit;
            orderCollection.fetch({
                data:$.param(contextModel.toParams()),
                remove:false});
            }
	    },
    });

    orderCollection = new OrderCollection;
    if(contextModel.get('userAuth')) {
    	//orderCollection.fetch({data:$.param(contextModel.toParams())});
        this.tried = 0;
        this.offset = 0;
        orderCollection.fetch({
            data:$.param(contextModel.toParams()),
            remove:true});
    }
    contextModel.on('change:patients', 
		    // this will be needed once the context filters things
		    function(cm) {
			if(true && cm.get('userAuth')) {
			    if (cm.get('patients')) {
				//orderCollection.fetch({data:$.param(contextModel.toParams())});
                this.tried = 0;
                this.offset = 0;
                orderCollection.fetch({
                    data:$.param(contextModel.toParams()),
                    remove:true});
			    } else {
				orderCollection.reset();
			    }
			}
		    }, orderCollection);
    //alertCollection.on('all', function(en) { console.log('alertCollection: '+en);});

    return orderCollection;
});
