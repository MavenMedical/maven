define([
    'jquery',
    'underscore',
    'backbone',
    'models/contextModel'
], function($, _, Backbone, contextModel){
    var RuleCollection = Backbone.Collection.extend({url: '/list'});

    ruleCollection = new RuleCollection;
    if(contextModel.get('auth')) {
	ruleCollection.fetch({data:$.param(contextModel.toParams())});
    }
    contextModel.on('change', 
		    function(cm) {
			if(cm.get('auth')) {
			    ruleCollection.fetch({data:$.param(contextModel.toParams())});
			}
		    }, ruleCollection);
    return ruleCollection;
});
