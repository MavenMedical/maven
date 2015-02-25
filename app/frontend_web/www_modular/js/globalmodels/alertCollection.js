define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'globalmodels/scrollCollection'
], function($, _, Backbone, contextModel, ScrollCollection) {
    AlertModel = Backbone.Model;

    //specify default categories here, leave blank to include all categories
    var categories = [];

    alertCollection = new ScrollCollection;
    alertCollection.url = function() {return '/alerts'+this.offset+'-'+(this.offset+this.limit);};
    alertCollection.model = AlertModel;
    alertCollection.limit = 5;
    alertCollection.extraData = {'categories': categories};
    alertCollection.context = function(){
      contextModel.on('change:patients change:encounter change:startdate change:enddate',
		    // this will be needed once the context filters things
		    function(cm) {
			if(cm.get('userAuth')) {
                var data = {};
                $.extend(data, contextModel.toParams(), alertCollection.extraData);
			    this.tried = 0;
			    this.offset=0;
			    alertCollection.fetch({
				data:$.param(data),
				remove:true});
			}
	    }, this);
    };
    alertCollection.initialize();

    return alertCollection;
});
