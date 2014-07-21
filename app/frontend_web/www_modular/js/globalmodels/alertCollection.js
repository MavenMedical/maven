define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'globalmodels/scrollCollection'
], function($, _, Backbone, contextModel, ScrollCollection) {
    AlertModel = Backbone.Model;

    //specify default categories here, leave blank to include all categories
    var categories = "categories=" ;//categories=cost&categories=test";

    alertCollection = new ScrollCollection;
    alertCollection.url = function() {return '/alerts'+this.offset+'-'+(this.offset+this.limit);};
    alertCollection.model = AlertModel;
    alertCollection.limit = 5;
    alertCollection.data = categories;
    alertCollection.context = function(){
      contextModel.on('change:patients change:encounter change:startdate change:enddate',
		    // this will be needed once the context filters things
		    function(cm) {
			if(cm.get('userAuth')) {
			    this.tried = 0;
			    this.offset=0;
			    alertCollection.fetch({
				data:$.param(contextModel.toParams())+"&"+categories,
				remove:true});
			}
	    }, this);
    };
    alertCollection.initialize();

    return alertCollection;
});
