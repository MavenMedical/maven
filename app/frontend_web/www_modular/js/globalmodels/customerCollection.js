define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'globalmodels/scrollCollection'
], function($, _, Backbone, contextModel, ScrollCollection) {
    CustomerModel = Backbone.Model;

    customerCollection = new ScrollCollection;
    customerCollection.url = function() {return '/customers'+this.offset+'-'+(this.offset+this.limit);};
    customerCollection.model = CustomerModel;
    customerCollection.limit = 10;
    customerCollection.context = function(){
        contextModel.on('change:startdate change:enddate',
		    // this will be needed once the context filters things
		    function(cm) {
			if(true && cm.get('customerAuth')) {
                this.tried = 0;
                this.offset = 0;
                customerCollection.fetch({
                    data:$.param(contextModel.toParams()),
                    remove:true});
			}
        }, customerCollection);
    };

    customerCollection.initialize();
    customerCollection.refresh = function() {
        if(contextModel.get('userAuth')) {
            this.tried = 0;
            this.offset = 0;
            customerCollection.fetch({
                data:$.param(contextModel.toParams()),
                remove:true});
        }
    };

    return customerCollection;
});
