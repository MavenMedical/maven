/**
 * Created by Asmaa Aljuhani on 7/5/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'globalmodels/histogramModel'
], function ($, _, Backbone, contextModel, histogramModel) {
    // This view is to show a histogram chart for how much is spent each day
    // Upon feedback, this wasn't intuitive and clear to use as datepicker
    var DatepickerChart = Backbone.View.extend({
        initialize: function (arg) {
            this.template = _.template(arg.template); // this must already be loaded
            histogramModel.on('change', this.update, this);
            contextModel.on('change page', this.update, this);

            this.$el.html(this.template(this));
            this.update();
        },
        update: function () {

            var data = [];
            for (var key in histogramModel.attributes) {
                var enc = histogramModel.attributes[key];
                data.push(enc);
            }

            var chart = AmCharts.makeChart("datepicker-chart", {
                "type": "serial",
                "theme": "light",
                "dataDateFormat": "YYYY-MM-DD",
                "pathToImages": "http://cdn.amcharts.com/lib/3/images/",
                "categoryField": "admission",
                "startDuration": 1,
                "categoryAxis": {
                    "gridPosition": "start"
                },
                "chartCursor": {},
                "chartScrollbar": {},
                "trendLines": [],
                "graphs": [
                    {
                        "fillAlphas": 1,
                        "id": "AmGraph-1",
                        "title": "graph 1",
                        "type": "column",
                        "valueField": "spending",
                        "balloonText": "[[diagnosis]] <br /><b>$[[value]]</b>",
                    }
                ],
                "guides": [],
                "valueAxes": [
                    {
                        "id": "ValueAxis-1",
                        "title": "Spending"
                    }
                ],
                "allLabels": [],
                "balloon": {
                },
                "chartScrollbar": {
                    //"autoGridCount": true,
                    "graph": "AmGraph-1",
                    "scrollbarHeight": 20
                },
                "dataProvider": data,
                periodSelector: {
                    position: "left",
                    periods: [
                        {
                            period: "MM",
                            selected: true,
                            count: 1,
                            label: "1 month"
                        },
                        {
                            period: "YYYY",
                            count: 1,
                            label: "1 year"
                        },
                        {
                            period: "YTD",
                            label: "YTD"
                        },
                        {
                            period: "MAX",
                            label: "MAX"
                        }
                    ]
                }
            });

            chart.addListener("clickGraphItem", function (e) {
                var eventData = e.item.dataContext;

                var URL;
                URL = "episode/" + eventData['encounterid'] + "/";
                URL += "patient/" + eventData['patientid'] + "/";
                URL += eventData['admission'];

                // navigate to the chosen encounter
                Backbone.history.navigate(URL, true);

                // hide the modal
                $('#datepicker-modal').modal('hide');
            });
            $("#datepicker-modal").on('shown.bs.modal', function () {
                chart.invalidateSize();
            });

        }
    });
    return DatepickerChart;
});
