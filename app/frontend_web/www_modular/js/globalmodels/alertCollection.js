define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel'
], function($, _, Backbone, contextModel) {
    AlertModel = Backbone.Model;

    var AlertCollection = Backbone.Collection.extend({
	url: '/alerts',
	model: AlertModel,
	initialize: function(){
            // nothing here yet
        },
    });

    alertCollection = new AlertCollection;
    if(contextModel.get('userAuth')) {
	alertCollection.fetch({data:$.param(contextModel.toParams())});
    }
    contextModel.on('change:patients', 
		    // this will be needed once the context filters things
		    function(cm) {
			if(true && cm.get('userAuth')) {
			    alertCollection.fetch({data:$.param(contextModel.toParams())});
			}
		    }, alertCollection);
    //alertCollection.on('all', function(en) { console.log('alertCollection: '+en);});

    return alertCollection;
});
