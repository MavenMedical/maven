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

    if(contextModel.get('userAuth')) {
	summaryModel.fetch({data:$.param(contextModel.toParams())});
    }
    contextModel.on('change:patients change:userAuth', 
		    function(x) {
			summaryModel.fetch({data:$.param(x.toParams())});
		    });
    
    return summaryModel;
});
