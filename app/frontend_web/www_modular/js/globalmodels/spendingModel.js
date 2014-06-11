/**
 * Created by Asmaa Aljuhani on 3/14/14.
 */

define([
    'underscore',
    'backbone',
    'globalmodels/contextModel'
], function (_, Backbone, contextModel) {

    var SpendingModel = Backbone.Model.extend({
	urlRoot: '/spending',
	clickType: function(type) {
	    this.set({typeFilter:type});
	},
	clickDate: function(x) {
	    var d=x.item.dataContext.date;
	    //console.log(d);
	    d.setHours(0);
	    d.setMinutes(0);
	    d.setSeconds(0);
	    d.setMilliseconds(0);
	    this.set({dateFilter:d});
	}
    });
    
    var spendingModel = new SpendingModel;
    spendingModel.set({'typeFilter':'', dateFilter:''});
    if(contextModel.get('userAuth')) {
	spendingModel.fetch({data:$.param(contextModel.toParams())});
    }
    contextModel.on('change:patients change:userAuth', 
		    function(x) {
			if(x.get('userAuth')) {
			    spendingModel.fetch({data:$.param(x.toParams())});
			}
		    });

    return spendingModel;
});
