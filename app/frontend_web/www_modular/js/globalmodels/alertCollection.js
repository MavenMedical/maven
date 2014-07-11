define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'globalmodels/scrollCollection'
], function($, _, Backbone, contextModel, ScrollCollection) {
    AlertModel = Backbone.Model;

    alertCollection = new ScrollCollection;
    alertCollection.url = function() {return '/alerts'+this.offset+'-'+(this.offset+this.limit);};
    alertCollection.model = AlertModel;
    alertCollection.limit = 5;
    alertCollection.context = function(){
      contextModel.on('change:patients change:encounter',
		    // this will be needed once the context filters things
		    function(cm) {
			if(cm.get('userAuth')) {
			    this.tried = 0;
			    this.offset=0;
			    alertCollection.fetch({
				data:$.param(contextModel.toParams()),
				remove:true});
			}
	    }, this);
    };
    alertCollection.initialize();

    return alertCollection;
});
