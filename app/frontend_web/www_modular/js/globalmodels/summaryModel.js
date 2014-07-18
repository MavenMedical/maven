/**
 * Created by Asmaa Aljuhani on 3/14/14.
 */

define([
    'jquery',
    'backbone',
    'globalmodels/contextModel'
], function ($, BackBone, contextModel) {

    var SummaryModel = Backbone.Model.extend({urlRoot: '/total_spend'});
    var summaryModel = new SummaryModel;

    summaryModel.set({'spending':'','savings':''}, {silent:true});
    if(contextModel.get('userAuth')) {
	summaryModel.fetch({data:$.param(contextModel.toParams())});
    }
    var lastchange = {};
    contextModel.on('change:patients change:userAuth change:encounter change:startdate change:enddate', 
		    function(x) {
			var changes = _.extend({},contextModel.changed);
			if(!_.isEqual(changes,lastchange)) {
			    lastchange = changes;
			    summaryModel.set({'spending':'','savings':''}, {silent:true});
			    summaryModel.fetch({data:$.param(x.toParams())});
			}
		    });
    
    return summaryModel;
});
