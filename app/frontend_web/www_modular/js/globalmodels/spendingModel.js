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
	},
	getGathered: function() {
	    var gathered = {};
	    var data = [];
	    var datefilter = this.get('dateFilter');
	    for (var d in this.attributes) {
		if(Date.parse(d)) {
		    var date = new Date(d);
		    if(!datefilter || 
		       (date.getFullYear()==datefilter.getFullYear() && 
			date.getMonth()==datefilter.getMonth() &&
			date.getDate()==datefilter.getDate())) {
			var days_spend = spendingModel.get(d);
			for (var t in days_spend) {
			    var base = days_spend[t];
			    if (t in gathered) {
				base = base + gathered[t];
			    }
			    gathered[t]=base;
			}
		    }
		}
	    }
	    return gathered;
	}
    });
    
    var spendingModel = new SpendingModel;
    spendingModel.set({'typeFilter':'', dateFilter:''});
    if(contextModel.get('userAuth')) {
	spendingModel.fetch({data:$.param(contextModel.toParams())});
    }
    contextModel.on('change:patients change:userAuth change:encounter change:startdate change:enddate', 
		    function(x) {
			if(x.get('userAuth')) {
			    spendingModel.fetch({
				data:$.param(x.toParams()),
				success: function(m,r) {
				    var old={
					'typeFilter':spendingModel.get('typeFilter'),
					'dateFilter':spendingModel.get('dateFilter')
				    };
				    spendingModel.clear({silent:true});
				    spendingModel.set($.extend(old,r));
				    console.log(spendingModel.attributes);
				},
			    });
			}
		    });

    return spendingModel;
});
