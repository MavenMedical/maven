/**
 * Created by Asmaa Aljuhani on 6/26/14.
 */
define([
    'jquery',
    'backbone',
    'globalmodels/contextModel'
], function ($, BackBone, contextModel) {

    var HistogramModel = Backbone.Model.extend({urlRoot: '/hist_spending'});
    var histogramModel = new HistogramModel;

    var downloadorder = ['diagnosis', 'admission', 'discharge', 'spending'];

    if(contextModel.get('userAuth')) {
	histogramModel.fetch({data:$.param(contextModel.toParams())});
    }
    contextModel.on('change:patients change:userAuth',
		    function(x) {
			histogramModel.fetch({data:$.param(x.toParams())});
		    });

    return histogramModel;
});