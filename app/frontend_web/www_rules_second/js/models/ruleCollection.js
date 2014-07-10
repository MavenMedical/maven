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


		    data:$.param(contextModel.toParams())
		});
	    }
	});

    var ruleCollection = new RuleCollection;

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
             var toUpdate = ruleModel.get('id')
		     ruleCollection.add(new Backbone.Model({name:ruleModel.get('name'),
							    id:ruleModel.get('id')}));

             _.each(ruleCollection.models, function(cur){
                 if (cur.get('id')==toUpdate){
                    cur.set({name: ruleModel.get('name')})
                 }
             }, this)
		 }, 
		 ruleCollection);


    return ruleCollection;
});
