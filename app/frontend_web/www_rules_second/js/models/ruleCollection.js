define([
    'jquery',
    'underscore',
    'backbone',
    'models/contextModel',
    'models/ruleModel'
], function($, _, Backbone, contextModel, ruleModel){
    var RuleCollection = Backbone.Collection.extend(
	{
	    url: '/list',
	    newFetch: function() {
		this.fetch({
		    data:$.param(contextModel.toParams()),
		});
	    }
	});

    ruleCollection = new RuleCollection;
    if(contextModel.get('auth')) {
	ruleCollection.newFetch();
    }
    contextModel.on('change:auth change:filter', 
		    function(cm) {
			if(cm.get('auth')) {
			    ruleCollection.newFetch();
			}
		    }, ruleCollection);
    
    ruleModel.on('sync',
		 function() {
		     ruleCollection.add(new Backbone.Model({name:ruleModel.get('name').get('name'),
							    id:ruleModel.get('id').get('id')}));
		 }, 
		 ruleCollection);

    return ruleCollection;
});
