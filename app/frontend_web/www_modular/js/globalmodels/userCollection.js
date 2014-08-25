define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'globalmodels/scrollCollection'
], function($, _, Backbone, contextModel, ScrollCollection) {
    UserModel = Backbone.Model;

    userCollection = new ScrollCollection;
    userCollection.url = function() {return '/users'+this.offset+'-'+(this.offset+this.limit);};
    userCollection.model = UserModel;
    userCollection.limit = 10;
    userCollection.context = function(){
        contextModel.on('change:patients change:encounter change:startdate change:enddate',
		    // this will be needed once the context filters things
		    function(cm) {
			if(true && cm.get('userAuth')) {
			    if (cm.get('patients')) {
                this.tried = 0;
                this.offset = 0;
                userCollection.fetch({
                    data:$.param(contextModel.toParams()),
                    remove:true});
			    } else {
				userCollection.reset();
			    }
			}
        }, userCollection);
    };

    userCollection.initialize();

    return userCollection;
});
