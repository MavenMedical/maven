define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'globalmodels/scrollCollection'
], function($, _, Backbone, contextModel, ScrollCollection) {
    OrderModel = Backbone.Model;

    orderCollection = new ScrollCollection;
    orderCollection.url = function() {return '/orders/'+this.offset+'-'+(this.offset+this.limit);};
    orderCollection.model = OrderModel;
    orderCollection.limit = 3;
    orderCollection.context = function(){
        contextModel.on('change:patients',
		    // this will be needed once the context filters things
		    function(cm) {
			if(true && cm.get('userAuth')) {
			    if (cm.get('patients')) {
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
    };

    orderCollection.initialize();

    return orderCollection;
});
