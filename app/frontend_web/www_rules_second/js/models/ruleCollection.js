/*a backbone model representing the collection of name, id pairs available to the rule editor, it does NOT contain
  the full contents of any rule, however you can fetch the full rule by placing one of the IDs into the context model

 */
define([
    'jquery',
    'underscore',
    'backbone',
    'models/contextModel',
    'models/ruleModel'
], function($, _, Backbone, contextModel, ruleModel){
    var RuleCollection = Backbone.Collection.extend(
	{
	    url: '/rulelist',

        newFetch: function() {
        alert()
		  	    this.fetch({


		    data:$.param(contextModel.toParams())
		});
	    }
	});

    var ruleCollection = new RuleCollection;

    if(contextModel.get('auth')) {



	ruleCollection.newFetch();
    }

    //load the persistance info when someone logs in
    contextModel.on('change:auth change:filter', 

		    function(cm) {
			if(cm.get('auth')) {
			    ruleCollection.newFetch();
			}
		    }, ruleCollection);

        //load the persistance info when the current rule is saved to the database
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
