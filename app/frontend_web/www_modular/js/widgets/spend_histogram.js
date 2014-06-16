/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
], function ($, _, Backbone, contextModel) {

    var HistogramModel = Backbone.Model.extend({urlRoot: '/hist_spending'});
    var histogramModel = new HistogramModel;

    if(contextModel.get('userAuth')) {
	histogramModel.fetch({data:$.param(contextModel.toParams())});
    }
    contextModel.on('change:patients change:userAuth', 
		    function(x) {
			histogramModel.fetch({data:$.param(x.toParams())});
		    });


    var HistogramView = Backbone.View.extend({
	initialize: function(arg) {
	    this.template = _.template(arg.template); // this must already be loaded
	    histogramModel.on('change', this.update, this);
	    contextModel.on('change page', this.update, this);
	    
	    this.update();
	},
	update: function() {
	    if(histogramModel.attributes && contextModel.get('page')=='home') {
		this.$el.html(this.template(contextModel.attributes));
		var values = _.pluck(histogramModel.attributes, 'spending');
		var max = _.max(values);
		var min = _.min(values);
		if(!this.binwidth) {
		    this.binwidth = (max-min) / 10;
		    if(!this.binwidth) {
			this.binwidth = 1000;
		    }
		}
		var binwidth = this.binwidth;
		console.log(binwidth);
		var start = binwidth * Math.floor(min/binwidth);
		var buckets = []
		for(var k=Math.floor((max-min)/binwidth); k>=0; k--) {
		    buckets[k]=0;
		}
		_.each(values, function(value) {
		    var bin = Math.floor((value-start)/binwidth);
		    buckets[bin]++;
		});
		console.log(buckets);
		buckets = _.map(buckets, function(v, k) {
		    return {'center':(binwidth+.5)*k, 'value':v};
		});
		console.log(buckets);
		AmCharts.makeChart('spend-histogram', {
		    "type": "serial",
		    "categoryField":"center",
		    "autoMarginOffset": 40,
		    "marginRight": 60,
		    "marginTop": 60,
		    "startDuration": 1,
		    "fontSize": 13,
		    "theme": "black",
		    "categoryAxis": {
			"gridPosition": "start"
		    },
		    "graphs": [{
			"type":"column",
			"valueField":"value",
			"fillAlphas": 1,
			"id": "AmGraph-1",
			"labelText": "",
			"title": "graph 1",
		    }],
		    "valueAxes": [
			{
			    "id": "ValueAxis-1",
			    "title": ""
			}
		    ],
		    "dataProvider":buckets,
		});
		this.$el.show();
	    } else {
		this.$el.hide();
	    }
	}
    });
    return HistogramView;
});

