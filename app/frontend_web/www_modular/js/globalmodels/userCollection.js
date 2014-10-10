define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'globalmodels/scrollCollection',
    ''
], function($, _, Backbone, contextModel, ScrollCollection) {
    UserModel = Backbone.Model;

    userCollection = new ScrollCollection;
    userCollection.url = function() {return '/users'+this.offset+'-'+(this.offset+this.limit);};
    userCollection.model = UserModel;
    userCollection.limit = 10;
    userCollection.target_customer = "";
    userCollection.context = function(){
        contextModel.on('change:startdate change:enddate',
		    // this will be needed once the context filters things
		    userCollection.refresh);
    };

    userCollection.initialize();
    userCollection.refresh = function() {
        if(contextModel.get('userAuth')) {
            userCollection.extraData = "";
            if (userCollection.target_customer != ""){
                userCollection.extraData = "&target_customer=" + userCollection.target_customer;
            }

            userCollection.tried = 0;
            userCollection.offset = 0;
	    userCollection.reset();
            userCollection.more();
	}
    };
    return userCollection;
});
