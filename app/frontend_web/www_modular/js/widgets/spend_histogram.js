/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'globalmodels/histogramModel'
], function ($, _, Backbone, contextModel, histogramModel) {

    var downloadorder = ['diagnosis', 'admission', 'discharge', 'spending'];

    var HistogramView = Backbone.View.extend({
        initialize: function (arg) {
            this.template = _.template(arg.template); // this must already be loaded
            histogramModel.on('change', this.update, this);
            contextModel.on('change page', this.update, this);

            this.update();
        },
        events: {
            'click #histogram-download': 'downloadhist',
        },
        downloadhist: function () {
            var csvContent = ["data:text/csv;charset=utf-8," + downloadorder.join(',')];
            _.each(histogramModel.attributes, function (row) {
                csvContent.push('"' + _.map(downloadorder, function (v) {
                    return row[v];
                }).join('","') + '"');
            });
            window.open(encodeURI(csvContent.join('\n')));
        },
        update: function () {
            if (histogramModel.attributes && contextModel.get('page') == 'home') {
                this.$el.html(this.template(contextModel.attributes));
                var values = _.pluck(histogramModel.attributes, 'spending');
                var max = _.max(values);
                var min = _.min(values);
                if (!this.binwidth) {
                    this.binwidth = 100 * Math.floor((max - min) / 1000);
                    if (!this.binwidth) {
                        this.binwidth = 1000;
                    }
                }
                var binwidth = this.binwidth;
                var start = binwidth * Math.floor(min / binwidth);
                var buckets = []
                for (var k = Math.floor((max - min) / binwidth); k >= 0; k--) {
                    buckets[k] = 0;
                }
                _.each(values, function (value) {
                    var bin = Math.floor((value - start) / binwidth);
                    buckets[bin]++;
                });
                buckets = _.map(buckets, function (v, k) {
                    var x = start + binwidth * k;
                    return {'center': x + '-' + (x + binwidth), 'value': v};
                });
                
                var chart = AmCharts.makeChart('spend-histogram', {
                    "type": "serial",
                    "categoryField": "center",
                    "autoMarginOffset": 40,
                    "marginRight": 60,
                    "marginTop": 60,
                    "startDuration": 1,
                    "fontSize": 13,
                    "theme": 'light',
                    "categoryAxis": {
                        "gridPosition": "start",
                        "labelRotation": 45
                    },
                    "graphs": [
                        {
                            "type": "column",
                            "valueField": "value",
                            "fillAlphas": 1,
                            "id": "AmGraph-1",
                            "labelText": "",
                            "title": "graph 1",
                        }
                    ],
                    "valueAxes": [
                        {
                            "id": "ValueAxis-1",
                            "title": "Encounters",
                            "integersOnly": true
                        }
                    ],
                    "dataProvider": buckets,
                });
                this.$el.show();
                chart.invalidateSize();
            } else {
                this.$el.hide();
            }
        }
    });
    return HistogramView;
});

