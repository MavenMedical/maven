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
             var rows = $('#rule-list tr')
             for (var c = 0 ; c<rows.length; c++){
                 var check = ($('.select-button', rows[c]))
                 var name = ruleModel.get('name');
                 if (check[0].innerHTML == ruleModel.get('name')){
                     var el = $(rows[c]);
                     ruleModel.on('change:id', function(){if (contextModel.get('name') != name) {el.css({'font-size': '100%'});}})
                     console.log(rows)
                     $(rows[c]).css({'font-size': '220%'});
                 }
             }
             _.each(ruleCollection.models, function(cur){
                 if (cur.get('id')==toUpdate){
                    cur.set({name: ruleModel.get('name')})
                 }
             }, this)
		 }, 
		 ruleCollection);


    return ruleCollection;
});
